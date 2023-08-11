import getpass
import os
import sys

import yaml
from deepdiff import DeepDiff
from yaml import UnsafeLoader

from config.DockerConfig import DockerConfig, CoreDockerConfig
from config.EnvVars import DOCKER_COMPOSE_FOLDER_PREFIX, RADIXDLT_NODE_KEY_PASSWORD, \
    POSTGRES_PASSWORD
from config.Renderer import Renderer
from github import github
from setup.AnsibleRunner import AnsibleRunner
from setup.BaseSetup import BaseSetup
from setup.DockerCommandArguments import DockerConfigArguments, DockerInstallArguments
from setup.GatewaySetup import GatewaySetup
from utils.Prompts import Prompts
from utils.utils import run_shell_command, Helpers, bcolors


def print_questionary_header(config_file):
    Helpers.section_headline("CONFIG FILE")
    print(
        "\nCreating config file using the answers from the questions that would be asked in next steps."
        f"\nLocation of the config file: {bcolors.OKBLUE}{config_file}{bcolors.ENDC}")


class DockerSetup(BaseSetup):

    @staticmethod
    def save_config(config: DockerConfig, config_file: str, autoapprove=False):
        to_update = ""
        if autoapprove:
            print("In Auto mode - Updating the file as suggested in above changes")
        else:
            to_update = input("\nOkay to update the config file [Y/n]?:")
        if Helpers.check_Yes(to_update) or autoapprove:
            print(f"Saving configuration to {config_file}")
            config.to_file(config_file)

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
                           'radixdlt/htpasswd:v1.1.0',
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
    def save_compose_file(existing_docker_compose: str, composefile_yaml: dict):
        with open(existing_docker_compose, 'w') as f:
            yaml.dump(composefile_yaml, f, default_flow_style=False, explicit_start=True, allow_unicode=True)

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
        if docker_config.gateway.enabled and not postgres_password:
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
    def conditionally_start_local_postgres(docker_config: DockerConfig):
        if docker_config.gateway.enabled:
            postgres_db = docker_config.gateway.postgres_db
            if DockerSetup.check_post_db_local(docker_config):
                cli_version = Helpers.cli_version()
                ansible_dir = f'https://raw.githubusercontent.com/radixdlt/babylon-nodecli/{cli_version}/node-runner-cli'
                AnsibleRunner(ansible_dir).run_setup_postgress(
                    postgres_db.password,
                    postgres_db.user,
                    postgres_db.dbname,
                    'ansible/project/provision.yml')

    @staticmethod
    def check_post_db_local(docker_config: DockerConfig):
        postgres_db = docker_config.gateway.postgres_db
        if postgres_db and postgres_db.setup == "local":
            return True
        return False

    @staticmethod
    def get_existing_compose_file(docker_config: DockerConfig) -> dict:
        compose_file = docker_config.common_config.docker_compose
        Helpers.section_headline("Checking if you have existing docker compose file")
        if os.path.exists(compose_file):
            return Helpers.yaml_as_dict(compose_file)
        else:
            Helpers.print_info("Seems you are creating docker compose file for first time")
            return None

    @staticmethod
    def exit_on_missing_trustednode():
        print("-t or --trustednode parameter is mandatory")
        sys.exit(1)

    @staticmethod
    def update_versions(docker_config: DockerConfig, autoapprove=False) -> DockerConfig:
        if docker_config.core_node:
            current_core_release = docker_config.core_node.core_release
            latest_core_release = github.latest_release("radixdlt/babylon-node")
            docker_config.core_node.core_release = Prompts.confirm_version_updates(current_core_release,
                                                                                   latest_core_release, 'CORE',
                                                                                   autoapprove)
        if docker_config.gateway.enabled:
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

    # @staticmethod
    # def backup_save_config(config_file, new_config, backup_time, autoapprove=False):
    #     to_update = ""
    #     if autoapprove:
    #         print("In Auto mode - Updating the file as suggested in above changes")
    #     else:
    #         to_update = input("\nOkay to update the config file [Y/n]?:")
    #     if Helpers.check_Yes(to_update) or autoapprove:
    #         if os.path.exists(config_file):
    #             print(f"\n\n Backing up existing config file")
    #             Helpers.backup_file(config_file, f"{config_file}_{backup_time}")
    #         print(f"\n\n Saving to file {config_file} ")
    #         with open(config_file, 'w') as f:
    #             yaml.dump(new_config, f, default_flow_style=False, explicit_start=True, allow_unicode=True)

    @staticmethod
    def load_settings(config_file) -> DockerConfig:
        if not os.path.isfile(config_file):
            print(f"No configuration found. Execute 'babylonnode docker config' first.")
            sys.exit(1)
        with open(config_file, 'r') as f:
            dictionary = yaml.load(f, Loader=UnsafeLoader)
        return DockerConfig(dictionary)

    @staticmethod
    def questionary(argument_object: DockerConfigArguments) -> DockerConfig:
        print_questionary_header(argument_object.config_file)
        docker_config = DockerConfig({})
        docker_config.core_node.core_release = argument_object.release
        print(
            "\nCreating config file using the answers from the questions that would be asked in next steps."
            f"\nLocation of the config file: {bcolors.OKBLUE}{argument_object.config_file}{bcolors.ENDC}")

        docker_config.common_config.ask_network_id(argument_object.networkid)
        docker_config.common_config.ask_existing_docker_compose_file()

        if "CORE" in argument_object.setupmode.mode:
            quick_node_settings: CoreDockerConfig = CoreDockerConfig({}).ask_config(argument_object.release,
                                                                                    argument_object.trustednode,
                                                                                    argument_object.keystore_password,
                                                                                    argument_object.new_keystore,
                                                                                    argument_object.validator)
            docker_config.core_node = quick_node_settings
            docker_config.common_config.ask_enable_nginx_for_core(argument_object.nginx_on_core)

        if "GATEWAY" in argument_object.setupmode.mode:
            docker_config.gateway = GatewaySetup.ask_gateway_full_docker(
                argument_object.postgrespassword, "http://core:3333/core")
            docker_config.common_config.ask_enable_nginx_for_gateway(argument_object.nginx_on_gateway)
        if "DETAILED" in argument_object.setupmode.mode:
            run_fullnode = Prompts.check_for_fullnode()
            if run_fullnode:
                detailed_node_settings: CoreDockerConfig = CoreDockerConfig({}).ask_config(
                    argument_object.release,
                    argument_object.trustednode,
                    argument_object.keystore_password,
                    argument_object.new_keystore,
                    argument_object.validator)
                docker_config.core_node = detailed_node_settings
                docker_config.common_config.ask_enable_nginx_for_core(argument_object.nginx_on_core)
            else:
                docker_config.common_config.nginx_settings.protect_core = "false"

            run_gateway = Prompts.check_for_gateway()
            if run_gateway:
                docker_config.gateway = GatewaySetup.ask_gateway_full_docker(argument_object.postgrespassword,
                                                                             argument_object.olympia_node_url)
                docker_config.common_config.ask_enable_nginx_for_gateway(argument_object.nginx_on_gateway)
            else:
                docker_config.common_config.nginx_settings.protect_gateway = "false"

        if "MIGRATION" in argument_object.setupmode.mode:
            docker_config.migration.ask_migration_config(argument_object.olympia_node_url,
                                                         argument_object.olympia_node_auth_user,
                                                         argument_object.olympia_node_auth_password,
                                                         argument_object.olympia_node_bech32_address)

        if docker_config.common_config.check_nginx_required():
            docker_config.common_config.ask_nginx_release()
            if docker_config.core_node.enable_transaction == "true":
                docker_config.common_config.nginx_settings.enable_transaction_api = "true"
            else:
                docker_config.common_config.nginx_settings.enable_transaction_api = "false"

        return docker_config

    @staticmethod
    def compare_config_file_with_config_object(config_file: str, config_object: DockerConfig):
        if os.path.exists(config_file):
            old_config: DockerConfig = DockerSetup.load_settings(config_file)
            if old_config is not None:
                print(f"""
                    {Helpers.section_headline("Differences")}
                    Difference between existing config file and new config that you are creating
                    {dict(DeepDiff(old_config, config_object.to_dict()))}
                      """)

    @staticmethod
    def print_config(configuration):
        config_dict: dict = configuration.to_dict()
        yaml.add_representer(type(None), Helpers.represent_none)
        Helpers.section_headline("CONFIG is Generated as below")
        print(f"\n{yaml.dump(config_dict)}")
        return config_dict

    @staticmethod
    def render_docker_compose(docker_config: DockerConfig):
        return Renderer().load_file_based_template("radix-fullnode-compose.yml.j2").render(
            docker_config.to_dict()).to_yaml()

    @staticmethod
    def confirm_config_changes(argument_object: DockerInstallArguments, docker_config, docker_config_updated_versions):
        config_differences = dict(DeepDiff(docker_config, docker_config_updated_versions))

        if len(config_differences) != 0:
            print(f"""
                      {Helpers.section_headline("Differences in config file with updated software versions")}
                      Difference between existing config file and new config that you are creating
                      {config_differences}
                        """)
            DockerSetup.save_config(docker_config_updated_versions, argument_object.config_file,
                                    argument_object.autoapprove)

    @staticmethod
    def confirm_docker_compose_file_changes(docker_config: DockerConfig, autoapprove: bool):
        docker_compose_yaml: yaml = DockerSetup.render_docker_compose(docker_config)
        backup_time = Helpers.get_current_date_time()
        compose_file_yaml = DockerSetup.get_existing_compose_file(docker_config)
        compose_file = docker_config.common_config.docker_compose
        if compose_file_yaml is not None:
            compose_file_yaml = {}
        compose_file_difference = dict(DeepDiff(compose_file_yaml, docker_compose_yaml))
        if len(compose_file_difference) != 0:
            print(f"""
                    {Helpers.section_headline("Differences between existing compose file and new compose file")}
                     Difference between existing compose file and new compose file that you are creating
                    {compose_file_difference}
                      """)
            to_update = ""
            if autoapprove:
                print("In Auto mode - Updating file as suggested in above changes")
            else:
                to_update = input("\nOkay to update the file [Y/n]?:")

            if Helpers.check_Yes(to_update) or autoapprove:
                if os.path.exists(compose_file):
                    Helpers.backup_file(compose_file, f"{compose_file}_{backup_time}")
                DockerSetup.save_compose_file(compose_file, docker_compose_yaml)
        run_shell_command(f"cat {compose_file}", shell=True)
        return compose_file

    @staticmethod
    def chown_files(docker_config: DockerConfig):
        import getpass
        username = getpass.getuser()
        run_shell_command(['sudo', 'chown', f'{username}:{username}',
                           f'{docker_config.core_node.keydetails.keyfile_path}/{docker_config.core_node.keydetails.keyfile_name}'])
        run_shell_command(['sudo', 'chown', f'{username}:{username}',
                           f'{docker_config.common_config.genesis_bin_data_file}'])
        run_shell_command(['sudo', 'chown', '-R', f'{username}:{username}',
                           f'{docker_config.core_node.data_directory}'])