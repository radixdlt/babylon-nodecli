import os
import sys
from pathlib import Path

import yaml
from deepdiff import DeepDiff
from yaml import UnsafeLoader

from config.EnvVars import UNZIPPED_NODE_DIST_FOLDER
from config.MigrationConfig import CommonMigrationConfig
from config.Renderer import Renderer
from config.SystemDConfig import SystemDConfig, CoreSystemdConfig, CommonSystemdConfig
from github import github
from setup.BaseSetup import BaseSetup
from setup.GatewaySetup import GatewaySetup
from setup.MigrationSetup import MigrationSetup
from setup.SystemDCommandArguments import SystemDConfigArguments
from utils.PromptFeeder import QuestionKeys
from utils.Prompts import Prompts
from utils.utils import run_shell_command, Helpers


class SystemDSetup(BaseSetup):

    @staticmethod
    def install_java():
        run_shell_command('sudo apt update', shell=True)
        run_shell_command('sudo apt install -y openjdk-17-jdk', shell=True)

    @staticmethod
    def setup_user():
        print("Checking if user radixdlt already exists")
        user_exists = run_shell_command("cat /etc/passwd | grep radixdlt", shell=True, fail_on_error=False)
        if user_exists.returncode != 0:
            run_shell_command('sudo useradd -m -s /bin/bash radixdlt', shell=True)
        run_shell_command(['sudo', 'usermod', '-aG', 'docker', 'radixdlt'])

    @staticmethod
    def create_service_user_password():
        run_shell_command('sudo passwd radixdlt', shell=True)

    @staticmethod
    def sudoers_instructions():
        print("""
            ----------------------------------------------------------------------------------------
            1. Execute following setups so that radixdlt user can use sudo commands without password

                $ sudo su 

                $ echo "radixdlt ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/radixdlt
        """)
        print("""
            2. After the above step logout.
             Then login using account radixdlt and the password you setup just now. To login using password, 
             you need to enable it in /etc/ssh/sshd_config.

             Instead, we suggest, for you to setup passwordless ssh login by copying the public key to
             /home/radixdlt/.ssh/authorized_keys

            3. Also one can change to another user by running sudo su command
                $ sudo su radixdlt
                $ cd /home/radixdlt

            ----------------------------------------------------------------------------------------
        """)

    @staticmethod
    def make_etc_directory():
        run_shell_command('sudo mkdir -p /etc/radixdlt/', shell=True)
        run_shell_command('sudo chown radixdlt:radixdlt -R /etc/radixdlt', shell=True)

    @staticmethod
    def make_data_directory():
        run_shell_command('sudo mkdir -p /babylon-ledger', shell=True)
        run_shell_command('sudo chown radixdlt:radixdlt -R /babylon-ledger', shell=True)

    @staticmethod
    def fetch_universe_json(trustenode, extraction_path):
        BaseSetup.fetch_universe_json(trustenode, extraction_path)

    @staticmethod
    def backup_file(filepath, filename, backup_time, auto_approve=False):
        if os.path.isfile(f"{filepath}/{filename}"):
            backup_yes = "Y"
            if auto_approve is None:
                backup_yes = input(f"{filename} file exists. Do you want to back up [Y/n]:")
            if Helpers.check_Yes(backup_yes) or auto_approve:
                Path(f"{backup_time}").mkdir(parents=True, exist_ok=True)
                run_shell_command(f"cp {filepath}/{filename} {backup_time}/{filename}", shell=True)

    @staticmethod
    def setup_service_file(settings: SystemDConfig,
                           service_file_path="/etc/systemd/system/radixdlt-node.service"):
        # This may need to be moved to jinja template
        tmp_service: str = "/tmp/radixdlt-node.service"
        Renderer().load_file_based_template("systemd.service.j2").render(settings.to_dict()).to_file(tmp_service)
        command = f"sudo mv {tmp_service} {service_file_path}"
        run_shell_command(command, shell=True)

    @staticmethod
    def download_binaries(binary_location_url, library_location_url, node_dir, node_version, auto_approve=None):
        run_shell_command(
            ['wget', '--no-check-certificate', '-O', 'babylon-node-dist.zip', binary_location_url])
        run_shell_command('unzip babylon-node-dist.zip', shell=True)
        run_shell_command(f'mkdir -p {node_dir}/{node_version}', shell=True)
        if os.listdir(f'{node_dir}/{node_version}'):
            if auto_approve is None:
                print(f"Directory {node_dir}/{node_version} is not empty")
                okay = input("Should the directory be removed [Y/n]?:")
            else:
                okay = "Y"
            if Helpers.check_Yes(okay):
                run_shell_command(f"rm -rf {node_dir}/{node_version}/*", shell=True)
        unzipped_folder_name = os.getenv(UNZIPPED_NODE_DIST_FOLDER, f"core-{node_version}")
        run_shell_command(f'mv {unzipped_folder_name}/* {node_dir}/{node_version}', shell=True)

        # Download and unzip library
        run_shell_command(
            ['wget', '--no-check-certificate', '-O', 'babylon-node-lib.zip', library_location_url])
        run_shell_command('unzip babylon-node-lib.zip', shell=True)
        run_shell_command(f'sudo mkdir -p /usr/lib/jni', shell=True)
        run_shell_command(f'sudo chown radixdlt:radixdlt /usr/lib/jni', shell=True)
        run_shell_command(f'sudo mv libcorerust.so /usr/lib/jni/libcorerust.so', shell=True)

    @staticmethod
    def start_node_service():
        run_shell_command('sudo chown radixdlt:radixdlt -R /etc/radixdlt', shell=True)
        run_shell_command('sudo systemctl start radixdlt-node.service', shell=True)
        run_shell_command('sudo systemctl enable radixdlt-node.service', shell=True)
        run_shell_command('sudo systemctl restart radixdlt-node.service', shell=True)

    @staticmethod
    def install_nginx():
        nginx_installed = run_shell_command("sudo service --status-all | grep nginx", shell=True, fail_on_error=False)
        if nginx_installed.returncode != 0:
            run_shell_command('sudo apt install -y nginx apache2-utils', shell=True)
            run_shell_command('sudo rm -rf /etc/nginx/{sites-available,sites-enabled}', shell=True)

    @staticmethod
    def make_nginx_secrets_directory():
        run_shell_command('sudo mkdir -p /etc/nginx/secrets', shell=True)

    @staticmethod
    def setup_nginx_config(nginx_config_location_url, node_type, nginx_etc_dir, backup_time, auto_approve=None):
        SystemDSetup.install_nginx()
        if node_type == "archivenode":
            conf_file = 'nginx-archive.conf'
        elif node_type == "fullnode":
            conf_file = 'nginx-fullnode.conf'
        else:
            print(f"Node type - {node_type} specificed should be either archivenode or fullnode")
            sys.exit(1)

        if auto_approve is None:
            backup_yes = input("Do you want to backup existing nginx config [Y/n]?:")
            if Helpers.check_Yes(backup_yes):
                Path(f"{backup_time}/nginx-config").mkdir(parents=True, exist_ok=True)
                run_shell_command(f"sudo cp -r {nginx_etc_dir} {backup_time}/nginx-config", shell=True)

        if auto_approve is None:
            continue_nginx = input("Do you want to continue with nginx setup [Y/n]?:")
        else:
            continue_nginx = "Y"
        if Helpers.check_Yes(continue_nginx):
            run_shell_command(
                ['wget', '--no-check-certificate', '-O', 'radixdlt-nginx.zip', nginx_config_location_url])
            run_shell_command(f'sudo unzip -o radixdlt-nginx.zip -d {nginx_etc_dir}', shell=True)
            run_shell_command(f'sudo mv {nginx_etc_dir}/{conf_file}  /etc/nginx/nginx.conf', shell=True)
            run_shell_command(f'sudo mkdir -p /var/cache/nginx/radixdlt-hot', shell=True)
            return True
        else:
            return False

    @staticmethod
    def create_ssl_certs(secrets_dir, auto_approve=None):
        SystemDSetup.make_nginx_secrets_directory()
        if os.path.isfile(f'{secrets_dir}/server.key') and os.path.isfile(f'{secrets_dir}/server.pem'):
            if auto_approve is None:
                print(f"Files  {secrets_dir}/server.key and os.path.isfile(f'{secrets_dir}/server.pem already exists")
                answer = input("Do you want to regenerate y/n :")
                if Helpers.check_Yes(answer):
                    run_shell_command(f"""
                         sudo openssl req  -nodes -new -x509 -nodes -subj '/CN=localhost' \
                          -keyout "{secrets_dir}/server.key" \
                          -out "{secrets_dir}/server.pem"
                         """, shell=True)
        else:

            run_shell_command(f"""
                 sudo openssl req  -nodes -new -x509 -nodes -subj '/CN=localhost' \
                  -keyout "{secrets_dir}/server.key" \
                  -out "{secrets_dir}/server.pem"
            """, shell=True)

        if os.path.isfile(f'{secrets_dir}/dhparam.pem'):
            if auto_approve is None:
                print(f"File {secrets_dir}/dhparam.pem already exists")
                answer = input("Do you want to regenerate y/n :")
                if Helpers.check_Yes(answer):
                    run_shell_command(f"sudo openssl dhparam -out {secrets_dir}/dhparam.pem  4096", shell=True)
        else:
            print("Generating a dhparam.pem file")
            run_shell_command(f"sudo openssl dhparam -out {secrets_dir}/dhparam.pem  4096", shell=True)

    @staticmethod
    def setup_nginx_password(secrets_dir, usertype, username, password=None):
        run_shell_command(f'sudo mkdir -p {secrets_dir}', shell=True)
        print('-----------------------------')
        print(f'Setting up nginx password for user of type {usertype}')
        run_shell_command(f'sudo touch {secrets_dir}/htpasswd.{usertype}', fail_on_error=True, shell=True)
        if password is None:
            run_shell_command(f'sudo htpasswd -c {secrets_dir}/htpasswd.{usertype} {username}', shell=True)
        else:
            run_shell_command(f'sudo htpasswd -b -c {secrets_dir}/htpasswd.{usertype} {username} {password}',
                              shell=True)
        print(
            f"""Setup NGINX_{usertype.upper()}_PASSWORD environment variable using below command . Replace the string 
            'nginx_password_of_your_choice' with your password 

            $ echo 'export NGINX_{usertype.upper()}_PASSWORD="nginx_password_of_your_choice"' >> ~/.bashrc
            $ source ~/.bashrc
            """)
        if username not in ["admin", "metrics", "superadmin"]:
            print(
                f"""
            echo 'export NGINX_{usertype.upper()}_USERNAME="{username}"' >> ~/.bashrc
            """
            )

    @staticmethod
    def start_nginx_service():
        run_shell_command(f'sudo systemctl start nginx', shell=True)
        run_shell_command('sudo systemctl enable nginx', shell=True)
        run_shell_command('sudo systemctl restart nginx', shell=True)

    @staticmethod
    def restart_nginx_service():
        run_shell_command('sudo systemctl daemon-reload', shell=True)
        run_shell_command('sudo systemctl restart nginx', shell=True)

    @staticmethod
    def stop_nginx_service():
        run_shell_command('sudo systemctl stop nginx', shell=True)
        run_shell_command('sudo systemctl disable nginx', shell=True)

    @staticmethod
    def checkUser():
        print("\nChecking the user is radixdlt")
        result = run_shell_command(f'whoami | grep radixdlt', shell=True, fail_on_error=False)
        if result.returncode != 0:
            print(" You are not logged as radixdlt user. Logout and login as radixdlt user")
            sys.exit(1)
        else:
            print("User on the terminal is radixdlt")

    @staticmethod
    def create_initial_service_file():
        run_shell_command("sudo touch /etc/systemd/system/radixdlt-node.service", shell=True)
        run_shell_command("sudo chown radixdlt:radixdlt /etc/systemd/system/radixdlt-node.service", shell=True)

    @staticmethod
    def restart_node_service():
        run_shell_command('sudo systemctl daemon-reload', shell=True)
        run_shell_command('sudo systemctl restart radixdlt-node.service', shell=True)

    @staticmethod
    def stop_node_service():
        run_shell_command('sudo systemctl stop radixdlt-node.service', shell=True)
        run_shell_command('sudo systemctl disable radixdlt-node.service', shell=True)

    @staticmethod
    def confirm_config(nodetype: str, release: str, node_binary_url: str, nginx_config_url: str, auto_approve):
        if auto_approve:
            return
        answer = Helpers.input_guestion(
            f"\nGoing to setup node type {nodetype} for version {release} from location {node_binary_url} and {nginx_config_url}. \n Do you want to continue Y/n:",
            QuestionKeys.continue_systemd_install)
        if not Helpers.check_Yes(answer):
            print(" Quitting ....")
            sys.exit(1)
        return

    @staticmethod
    def save_config(settings: SystemDConfig, config_file: str, autoapprove=False):
        to_update = ""
        if autoapprove:
            print("In Auto mode - Updating the file as suggested in above changes")
        else:
            to_update = input("\nOkay to update the config file [Y/n]?:")
        if Helpers.check_Yes(to_update) or autoapprove:
            print(f"Saving configuration to {config_file}")
            settings.to_file(config_file)

    @staticmethod
    def load_settings(config_file) -> SystemDConfig:
        if not os.path.isfile(config_file):
            print(f"No configuration found. Execute 'babylonnode systemd config' first.")
            sys.exit(1)
        with open(config_file, 'r') as f:
            dictionary = yaml.load(f, Loader=UnsafeLoader)
        return SystemDConfig(dictionary)

    @staticmethod
    def compare_old_and_new_config(config_file: str, systemd_config: SystemDConfig):
        old_config_object = SystemDSetup.load_settings(config_file)
        old_config = old_config_object.to_dict()
        config_to_dump = systemd_config.to_dict()
        if old_config is not None:
            if len(old_config) != 0:
                print(f"""
                        {Helpers.section_headline("Differences")}
                        Difference between existing config file and new config that you are creating
                        {dict(DeepDiff(old_config, config_to_dump))}
                          """)

    @staticmethod
    def update_versions(systemd_config: SystemDConfig, autoapprove=False) -> SystemDConfig:
        if hasattr(systemd_config, "core_node"):
            current_core_release = systemd_config.core_node.core_release
            latest_core_release = github.latest_release("radixdlt/babylon-node")
            systemd_config.core_node.core_release = Prompts.confirm_version_updates(current_core_release,
                                                                                    latest_core_release, 'CORE',
                                                                                    autoapprove)
            systemd_config.core_node.generate_download_urls()
        if hasattr(systemd_config, "gateway") and systemd_config.gateway.enabled:
            latest_gateway_release = github.latest_release("radixdlt/babylon-gateway")
            current_gateway_release = systemd_config.gateway.data_aggregator.release

            if hasattr(systemd_config.gateway, "data_aggregator"):
                systemd_config.gateway.data_aggregator.release = Prompts.confirm_version_updates(
                    current_gateway_release,
                    latest_gateway_release, 'AGGREGATOR', autoapprove)

            if hasattr(systemd_config.gateway, "gateway_api"):
                systemd_config.gateway.gateway_api.release = Prompts.confirm_version_updates(
                    current_gateway_release,
                    latest_gateway_release, 'GATEWAY', autoapprove)

            if hasattr(systemd_config.gateway, "database_migration"):
                systemd_config.gateway.database_migration.release = Prompts.confirm_version_updates(
                    current_gateway_release,
                    latest_gateway_release, 'DATABASE MIGRATION', autoapprove)

        if hasattr(systemd_config.common_config, "nginx_settings"):
            latest_nginx_release = github.latest_release("radixdlt/babylon-nginx")
            current_nginx_release = systemd_config.common_config.nginx_settings.release
            systemd_config.common_config.nginx_settings.release = Prompts.confirm_version_updates(
                current_nginx_release, latest_nginx_release, "RADIXDLT NGINX", autoapprove
            )
            systemd_config.common_config.nginx_settings.generate_nginx_config_url()

        return systemd_config

    @staticmethod
    def dump_config_as_yaml(systemd_config: SystemDConfig):
        config_to_dump = {"common_config": systemd_config.common_config.to_dict(), "version": "0.1"}
        if hasattr(systemd_config, "core_node"):
            config_to_dump["core_node"] = systemd_config.core_node.to_dict()
        if hasattr(systemd_config, "gateway"):
            config_to_dump["gateway"] = systemd_config.gateway.to_dict()
        if hasattr(systemd_config, "migration"):
            config_to_dump["migration"] = systemd_config.migration.to_dict()

        yaml.add_representer(type(None), Helpers.represent_none)
        Helpers.section_headline("CONFIG is Generated as below")
        print(f"\n{yaml.dump(config_to_dump)}")
        return config_to_dump

    @staticmethod
    def ask_common_config(argument_object: SystemDConfigArguments) -> CommonSystemdConfig:
        systemd_config = SystemDConfig({})
        systemd_config.common_config.ask_network_id(argument_object.networkid)
        systemd_config.common_config.ask_host_ip(argument_object.hostip)
        systemd_config.common_config.ask_enable_nginx_for_core(argument_object.nginx_on_core)
        systemd_config.common_config.ask_nginx_release()
        return systemd_config.common_config

    @staticmethod
    def ask_core_node(argument_object: SystemDConfigArguments) -> CoreSystemdConfig:
        systemd_config = SystemDConfig({})

        systemd_config.core_node.set_core_release(argument_object.release)
        systemd_config.core_node.set_trusted_node(argument_object.trustednode)
        systemd_config.core_node.generate_download_urls()
        systemd_config.core_node.keydetails = BaseSetup.ask_keydetails(argument_object.keystore_password,
                                                                       argument_object.new_keystore)
        systemd_config.core_node.ask_data_directory(argument_object.data_directory)
        systemd_config.core_node.ask_validator_address(argument_object.validator)
        return systemd_config.core_node

    @staticmethod
    def ask_migration(argument_object: SystemDConfigArguments) -> CommonMigrationConfig:
        systemd_config = SystemDConfig({})
        if "MIGRATION" in argument_object.setupmode.mode:
            systemd_config = MigrationSetup.ask_migration_config(systemd_config, argument_object.olympia_node_url,
                                                                 argument_object.olympia_node_auth_user,
                                                                 argument_object.olympia_node_auth_password,
                                                                 argument_object.olympia_node_bech32_address)
        return systemd_config.migration

    @staticmethod
    def print_config(settings):
        print("--------------------------------")
        print("\nUsing following configuration:")
        print("\n--------------------------------")
        print(settings.to_yaml())

    @staticmethod
    def install_systemd_service(settings: SystemDConfig, args):
        SystemDSetup.print_config(settings)

        SystemDSetup.confirm_config(settings.core_node.nodetype,
                                    settings.core_node.core_release,
                                    settings.core_node.core_binary_url,
                                    settings.common_config.nginx_settings.config_url,
                                    args.auto)

        SystemDSetup.checkUser()

        SystemDSetup.download_binaries(binary_location_url=settings.core_node.core_binary_url,
                                       library_location_url=settings.core_node.core_library_url,
                                       node_dir=settings.core_node.node_dir,
                                       node_version=settings.core_node.core_release,
                                       auto_approve=args.auto)

        # default.conf file

        backup_time = Helpers.get_current_date_time()
        SystemDSetup.backup_file(settings.core_node.node_dir, f"default.config", backup_time, args.auto)
        settings.create_default_config_file(args.advanceduserconfig)

        # environment file
        SystemDSetup.backup_file(settings.core_node.node_secrets_dir, "environment", backup_time, args.auto)
        settings.create_environment_file()

        # radixdlt-node.service file
        SystemDSetup.backup_file("/etc/systemd/system", "radixdlt-node.service", backup_time, args.auto)
        if args.manual:
            service_file_path = f"{settings.core_node.node_dir}/radixdlt-node.service"
        else:
            service_file_path = "/etc/systemd/system/radixdlt-node.service"
        settings.create_service_file(service_file_path)

        SystemDSetup.chown_files(settings)
        # Nginx
        nginx_configured = SystemDSetup.setup_nginx_service(settings, backup_time, args.auto)

        # Gateway
        GatewaySetup.conditionally_install_local_postgreSQL(settings.gateway)
        GatewaySetup.conditionaly_install_standalone_gateway(settings, args.auto)

        if not args.manual:
            if not args.update:
                SystemDSetup.start_node_service()
            else:
                SystemDSetup.restart_node_service()

            if nginx_configured:
                SystemDSetup.start_nginx_service()
            else:
                print("Nginx not configured or not updated.")

    @staticmethod
    def chown_files(settings):
        run_shell_command(['sudo', 'chown', 'radixdlt:radixdlt',
                           f'{settings.core_node.keydetails.keyfile_path}/{settings.core_node.keydetails.keyfile_name}'])
        if settings.common_config.genesis_bin_data_file is not None:
            run_shell_command(['sudo', 'chown', 'radixdlt:radixdlt',
                               f'{settings.common_config.genesis_bin_data_file}'])
        run_shell_command(['sudo', 'chown', '-R', 'radixdlt:radixdlt',
                           f'{settings.core_node.node_secrets_dir}'])
        run_shell_command(['sudo', 'chown', '-R', 'radixdlt:radixdlt',
                           f'{settings.core_node.data_directory}'])

    @staticmethod
    def setup_nginx_service(settings: SystemDConfig, backup_time: str, autoapprove: bool):
        SystemDSetup.backup_file("/lib/systemd/system", "nginx.service", backup_time, autoapprove)
        SystemDSetup.create_ssl_certs(settings.common_config.nginx_settings.secrets_dir, autoapprove)
        nginx_configured = SystemDSetup.setup_nginx_config(
            nginx_config_location_url=settings.common_config.nginx_settings.config_url,
            node_type=settings.core_node.nodetype,
            nginx_etc_dir=settings.common_config.nginx_settings.dir, backup_time=backup_time,
            auto_approve=autoapprove)
        return nginx_configured

    @staticmethod
    def verify_memory_settings_migration(settings: SystemDConfig):
        if settings != None:
            if settings.migration != None:
                if settings.migration.use_olympia:
                    if "-Xms12g -Xmx12g" in settings.core_node.java_opts:
                        if Prompts.ask_temporary_java_opts_update():
                            settings.core_node.java_opts = "--enable-preview -server -Xms12g -Xmx12g  " \
                                                           "-XX:MaxDirectMemorySize=2048m " \
                                                           "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops " \
                                                           "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts " \
                                                           "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom " \
                                                           "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"
        return settings
