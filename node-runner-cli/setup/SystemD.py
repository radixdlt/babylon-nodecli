import os
import sys
from pathlib import Path

import yaml
from yaml import UnsafeLoader

from config.Renderer import Renderer
from config.SystemDConfig import SystemDSettings, from_dict
from env_vars import UNZIPPED_NODE_DIST_FOLDER
from setup.Base import Base
from utils.PromptFeeder import QuestionKeys
from utils.utils import run_shell_command, Helpers


class SystemD(Base):

    @staticmethod
    def install_java():
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
        # TODO AutoApprove
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
        run_shell_command('sudo mkdir -p /data', shell=True)
        run_shell_command('sudo chown radixdlt:radixdlt -R /data', shell=True)

    @staticmethod
    def fetch_universe_json(trustenode, extraction_path):
        Base.fetch_universe_json(trustenode, extraction_path)

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
    def setup_service_file(settings: SystemDSettings,
                           service_file_path="/etc/systemd/system/radixdlt-node.service"):
        # This may need to be moved to jinja template
        tmp_service: str = "/tmp/radixdlt-node.service"
        Renderer().load_file_based_template("systemd.service.j2").render(dict(settings)).to_file(tmp_service)
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
        run_shell_command(f'mkdir -p /usr/lib/jni', shell=True)
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
        SystemD.install_nginx()
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
        SystemD.make_nginx_secrets_directory()
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
    def confirm_config(nodetype, release, node_binary_url, nginx_config_url) -> str:
        answer = Helpers.input_guestion(
            f"\nGoing to setup node type {nodetype} for version {release} from location {node_binary_url} and {nginx_config_url}. \n Do you want to continue Y/n:",
            QuestionKeys.continue_systemd_install)
        if not Helpers.check_Yes(answer):
            print(" Quitting ....")
            sys.exit(1)
        return answer

    @staticmethod
    def save_settings(settings: SystemDSettings, config_file: str, autoapprove=False):
        to_update = ""
        if autoapprove:
            print("In Auto mode - Updating the file as suggested in above changes")
        else:
            to_update = input("\nOkay to update the config file [Y/n]?:")
        if Helpers.check_Yes(to_update) or autoapprove:
            print(f"Saving configuration to {config_file}")
            settings.to_file(config_file)

    @staticmethod
    def load_settings(config_file) -> SystemDSettings:
        if not os.path.isfile(config_file):
            print(f"No configuration found. Execute 'radixnode systemd config' first.")
            sys.exit(1)
        with open(config_file, 'r') as f:
            dictionary = yaml.load(f, Loader=UnsafeLoader)
        return from_dict(dictionary)
