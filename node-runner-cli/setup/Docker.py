import getpass
import os
import sys
from typing import Tuple, Dict, Any

import yaml
from yaml import UnsafeLoader

from config.DockerConfig import DockerConfig, from_dict
from env_vars import DOCKER_COMPOSE_FOLDER_PREFIX, COMPOSE_HTTP_TIMEOUT, RADIXDLT_NODE_KEY_PASSWORD, POSTGRES_PASSWORD
from github import github
from setup.AnsibleRunner import AnsibleRunner
from setup.Base import Base
from utils.Prompts import Prompts
from utils.utils import run_shell_command, Helpers


class Docker(Base):

    @staticmethod
    def setup_nginx_Password(usertype, username, password=None):
        print('-----------------------------')
        print(f'Setting up nginx user of type {usertype} with username {username}')
        if not password:
            nginx_password = getpass.getpass(f"Enter your nginx the password: ")
        else:
            nginx_password = password
        docker_compose_folder_prefix = os.getenv(DOCKER_COMPOSE_FOLDER_PREFIX, os.getcwd().rsplit('/', 1)[-1])
        run_shell_command(['docker', 'run', '--rm', '-v',
                           docker_compose_folder_prefix + '_nginx_secrets:/secrets',
                           'radixdlt/htpasswd:v1.0.0',
                           'htpasswd', '-bc', f'/secrets/htpasswd.{usertype}', username, nginx_password])

        print(
            f"""
            Setup NGINX_{usertype.upper()}_PASSWORD environment variable using below command . Replace the string 'nginx_password_of_your_choice' with your password

            echo 'export NGINX_{usertype.upper()}_PASSWORD="nginx_password_of_your_choice"' >> ~/.bashrc
            """)
        if username not in ["admin", "metrics", "superadmin"]:
            print(
                f"""
            echo 'export NGINX_{usertype.upper()}_USERNAME="{username}"' >> ~/.bashrc
            """
            )
        return nginx_password

    @staticmethod
    def run_docker_compose_up(composefile):
        docker_compose_binary = os.getenv("DOCKER_COMPOSE_LOCATION", 'docker-compose')
        result = run_shell_command([docker_compose_binary, '-f', composefile, 'up', '-d'],
                                   env={
                                       COMPOSE_HTTP_TIMEOUT: os.getenv(COMPOSE_HTTP_TIMEOUT, "200")
                                   }, fail_on_error=False)
        if result.returncode != 0:
            run_shell_command([docker_compose_binary, '-f', composefile, 'up', '-d'],
                              env={
                                  COMPOSE_HTTP_TIMEOUT: os.getenv(COMPOSE_HTTP_TIMEOUT, "200")
                              }, fail_on_error=True)

    @staticmethod
    def save_compose_file(existing_docker_compose: str, composefile_yaml: dict):
        with open(existing_docker_compose, 'w') as f:
            yaml.dump(composefile_yaml, f, default_flow_style=False, explicit_start=True, allow_unicode=True)

    @staticmethod
    def run_docker_compose_down(composefile, removevolumes=False):
        Helpers.docker_compose_down(composefile, removevolumes)

    @staticmethod
    def check_set_passwords(docker_config: DockerConfig):
        keystore_password = docker_config.core_node.keydetails.keystore_password
        if docker_config.core_node and not keystore_password:
            keystore_password_from_env = os.getenv(RADIXDLT_NODE_KEY_PASSWORD, None)
            if not keystore_password_from_env:
                print(
                    "Cannot find Keystore password either in config "
                    "or as environment variable RADIXDLT_NODE_KEY_PASSWORD")
                sys.exit(1)
            else:
                docker_config.core_node.keydetails.keystore_password = keystore_password_from_env

        postgres_password = docker_config.gateway.postgres_db.password
        if docker_config.gateway and not postgres_password:
            postgres_password_from_env = os.getenv(POSTGRES_PASSWORD, None)

            if not postgres_password_from_env:
                print(
                    "Cannot find POSTGRES_PASSWORD either in config"
                    "or as environment variable POSTGRES_PASSWORD")
                sys.exit(1)
            else:
                docker_config.gateway.postgres_db.password = postgres_password_from_env
        return docker_config

    @staticmethod
    def check_run_local_postgreSQL(docker_config: DockerConfig):
        postgres_db = docker_config.gateway.postgres_db
        if Docker.check_post_db_local(docker_config):
            ansible_dir = f'https://raw.githubusercontent.com/radixdlt/babylon-nodecli/{Helpers.cli_version()}/node-runner-cli'
            AnsibleRunner(ansible_dir).run_setup_postgress(
                postgres_db.get("password"),
                postgres_db.get("user"),
                postgres_db.get("dbname"),
                'ansible/project/provision.yml')

    @staticmethod
    def check_post_db_local(docker_config: DockerConfig):
        postgres_db = docker_config.gateway.postgres_db
        if postgres_db and postgres_db.get("setup", None) == "local":
            return True
        return False

    @staticmethod
    def get_existing_compose_file(docker_config: DockerConfig) -> Tuple[str, dict]:
        compose_file = docker_config.common_config.docker_compose
        Helpers.section_headline("Checking if you have existing docker compose file")
        if os.path.exists(compose_file):
            return compose_file, Helpers.yaml_as_dict(compose_file)
        else:
            Helpers.print_info("Seems you are creating docker compose file for first time")
            return compose_file, dict({})

    @staticmethod
    def exit_on_missing_trustednode():
        print("-t or --trustednode parameter is mandatory")
        sys.exit(1)

    @staticmethod
    def update_versions(docker_config: DockerConfig, autoapprove=False):
        if docker_config.core_node:
            current_core_release = docker_config.core_node.core_release
            latest_core_release = github.latest_release("radixdlt/babylon-node")
            docker_config.core_node.core_release = Prompts.confirm_version_updates(current_core_release,
                                                                                   latest_core_release, 'CORE',
                                                                                   autoapprove)
        if docker_config.gateway:
            latest_gateway_release = github.latest_release("radixdlt/babylon-gateway")
            current_gateway_release = docker_config.gateway.data_aggregator.release

            if docker_config.gateway.data_aggregator:
                docker_config.gateway.data_aggregator.release = Prompts.confirm_version_updates(
                    current_gateway_release,
                    latest_gateway_release, 'AGGREGATOR', autoapprove)

            if docker_config.gateway.gateway_api:
                docker_config.gatewa.gateway_api.release = Prompts.confirm_version_updates(
                    current_gateway_release,
                    latest_gateway_release, 'GATEWAY', autoapprove)

        if docker_config.common_config.nginx_settings:
            latest_nginx_release = github.latest_release("radixdlt/babylon-nginx")
            current_nginx_release = docker_config['common_config']["nginx_settings"]["release"]
            docker_config.common_config.nginx_settings.release = Prompts.confirm_version_updates(
                current_nginx_release, latest_nginx_release, "RADIXDLT NGINX", autoapprove
            )

        return docker_config

    @staticmethod
    def backup_save_config(config_file, new_config, backup_time, autoapprove=False):
        to_update = ""
        if autoapprove:
            print("In Auto mode - Updating the file as suggested in above changes")
        else:
            to_update = input("\nOkay to update the config file [Y/n]?:")
        if Helpers.check_Yes(to_update) or autoapprove:
            if os.path.exists(config_file):
                print(f"\n\n Backing up existing config file")
                Helpers.backup_file(config_file, f"{config_file}_{backup_time}")
            print(f"\n\n Saving to file {config_file} ")
            with open(config_file, 'w') as f:
                yaml.dump(new_config, f, default_flow_style=False, explicit_start=True, allow_unicode=True)

    @staticmethod
    def load_settings(config_file) -> DockerConfig:
        if not os.path.isfile(config_file):
            print(f"No configuration found. Execute 'babylonnode systemd config' first.")
            sys.exit(1)
        with open(config_file, 'r') as f:
            dictionary = yaml.load(f, Loader=UnsafeLoader)
        return from_dict(dictionary)
