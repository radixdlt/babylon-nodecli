import os
import sys
from pathlib import Path

import yaml
from yaml import UnsafeLoader

from config.SystemDConfig import SystemDSettings
from config.KeyDetails import KeyDetails
from env_vars import UNZIPPED_NODE_DIST_FOLDER, APPEND_DEFAULT_CONFIG_OVERIDES, NODE_BINARY_OVERIDE, \
    NGINX_BINARY_OVERIDE
from github.github import latest_release
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
            run_shell_command('sudo useradd -m -s /bin/bash radixdlt ', shell=True)
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
    def generatekey(keyfile_path, keyfile_name="node-keystore.ks", keygen_tag="1.0.0", keystore_password=None,
                    new=False):
        run_shell_command(f'mkdir -p {keyfile_path}', shell=True)
        keystore_password, keyfile_location = Base.generatekey(keyfile_path, keyfile_name, keygen_tag,
                                                               keystore_password, new)

        key_details = KeyDetails({})
        key_details.keystore_password = keystore_password
        key_details.keyfile_name = keyfile_name
        key_details.keygen_tag = keygen_tag
        key_details.keyfile_path = keyfile_path
        return key_details

    @staticmethod
    def fetch_universe_json(trustenode, extraction_path):
        Base.fetch_universe_json(trustenode, extraction_path)

    @staticmethod
    def backup_file(filepath, filename, backup_time, auto_approve=False):
        if os.path.isfile(f"{filepath}/{filename}"):
            backup_yes = "Y"
            if not auto_approve:
                backup_yes = input(f"{filename} file exists. Do you want to back up [Y/n]:")
            if Helpers.check_Yes(backup_yes) or auto_approve:
                Path(f"{backup_time}").mkdir(parents=True, exist_ok=True)
                run_shell_command(f"cp {filepath}/{filename} {backup_time}/{filename}", shell=True)

    @staticmethod
    def set_environment_variables(keystore_password, node_secrets_dir):
        command = f"""
cat > {node_secrets_dir}/environment << EOF
JAVA_OPTS="--enable-preview -server -Xms8g -Xmx8g  -XX:MaxDirectMemorySize=2048m -XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts -Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom -DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"
RADIX_NODE_KEYSTORE_PASSWORD={keystore_password}
        """
        run_shell_command(command, shell=True)

    @staticmethod
    def setup_default_config(trustednode, hostip, node_dir, node_type, keyfile_location="/etc/radixdlt/node/secrets",
                             keyfile_name="node-keystore.ks",
                             transactions_enable="false",
                             network_id=1,
                             data_folder="~/data"):

        genesis_json_location = Base.path_to_genesis_json(network_id)

        network_genesis_file_for_testnets = f"network.genesis_file={genesis_json_location}" if genesis_json_location else ""
        enable_client_api = "true" if node_type == "archivenode" else "false"

        command = f"""
        cat > {node_dir}/default.config << EOF
            ntp=false
            ntp.pool=pool.ntp.org
            network.id={network_id}
            {network_genesis_file_for_testnets}
            node.key.path={keyfile_location}/{keyfile_name}
            network.p2p.listen_port=30001
            network.p2p.broadcast_port=30000
            network.p2p.seed_nodes={trustednode}
            network.host_ip={hostip}
            db.location={data_folder}
            api.port=3334
            log.level=debug
            api.transactions.enable={"true" if transactions_enable else "false"}
            api.sign.enable=true 
            api.bind.address=0.0.0.0 
            network.p2p.use_proxy_protocol=false

        """
        run_shell_command(command, shell=True)

        if (os.getenv(APPEND_DEFAULT_CONFIG_OVERIDES)) is not None:
            print("Add overides")
            lines = []
            while True:
                line = input()
                if line:
                    lines.append(line)
                else:
                    break
            for text in lines:
                run_shell_command(f"echo {text} >> {node_dir}/default.config", shell=True)

    @staticmethod
    def setup_service_file(node_version_dir, node_dir="/etc/radixdlt/node",
                           node_secrets_path="/etc/radixdlt/node/secrets",
                           service_file_path="/etc/systemd/system/radixdlt-node.service"):

        command = f"""
        sudo cat > {service_file_path} << EOF
            [Unit]
            Description=Radix DLT Validator
            After=local-fs.target
            After=network-online.target
            After=nss-lookup.target
            After=time-sync.target
            After=systemd-journald-dev-log.socket
            Wants=network-online.target

            [Service]
            EnvironmentFile={node_secrets_path}/environment
            User=radixdlt
            LimitNOFILE=65536
            LimitNPROC=65536
            LimitMEMLOCK=infinity
            WorkingDirectory={node_dir}
            ExecStart={node_dir}/{node_version_dir}/bin/radixdlt
            SuccessExitStatus=143
            TimeoutStopSec=10
            Restart=on-failure

            [Install]
            WantedBy=multi-user.target
        """
        run_shell_command(command, shell=True)

    @staticmethod
    def download_binaries(binary_location_url, node_dir, node_version, auto_approve=None):
        run_shell_command(
            ['wget', '--no-check-certificate', '-O', 'radixdlt-dist.zip', binary_location_url])
        run_shell_command('unzip radixdlt-dist.zip', shell=True)
        run_shell_command(f'mkdir -p {node_dir}/{node_version}', shell=True)
        if os.listdir(f'{node_dir}/{node_version}'):
            if not auto_approve:
                print(f"Directory {node_dir}/{node_version} is not empty")
                okay = input("Should the directory be removed [Y/n]?:")
            else:
                okay = "Y"
            if Helpers.check_Yes(okay):
                run_shell_command(f"rm -rf {node_dir}/{node_version}/*", shell=True)
        unzipped_folder_name = os.getenv(UNZIPPED_NODE_DIST_FOLDER, f"radixdlt-{node_version}")
        run_shell_command(f'mv {unzipped_folder_name}/* {node_dir}/{node_version}', shell=True)

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
    def setup_nginx_config(nginx_config_location_Url, node_type, nginx_etc_dir, backup_time, auto_approve=None):
        SystemD.install_nginx()
        if node_type == "archivenode":
            conf_file = 'nginx-archive.conf'
        elif node_type == "fullnode":
            conf_file = 'nginx-fullnode.conf'
        else:
            print(f"Node type - {node_type} specificed should be either archivenode or fullnode")
            sys.exit()

        if not auto_approve:
            backup_yes = input("Do you want to backup existing nginx config [Y/n]?:")
            if Helpers.check_Yes(backup_yes):
                Path(f"{backup_time}/nginx-config").mkdir(parents=True, exist_ok=True)
                run_shell_command(f"sudo cp -r {nginx_etc_dir} {backup_time}/nginx-config", shell=True)

        if not auto_approve:
            continue_nginx = input("Do you want to continue with nginx setup [Y/n]?:")
        else:
            continue_nginx = "Y"
        if Helpers.check_Yes(continue_nginx) or auto_approve:
            additional_options = ""
            if auto_approve:
                additional_options = "-o"
            run_shell_command(
                ['wget', '--no-check-certificate', '-O', 'radixdlt-nginx.zip', nginx_config_location_Url])
            run_shell_command(f'sudo unzip {additional_options} radixdlt-nginx.zip -d {nginx_etc_dir}', shell=True)
            run_shell_command(f'sudo mv {nginx_etc_dir}/{conf_file}  /etc/nginx/nginx.conf', shell=True)
            run_shell_command(f'sudo mkdir -p /var/cache/nginx/radixdlt-hot', shell=True)
            return True
        else:
            return False

    @staticmethod
    def create_ssl_certs(secrets_dir, auto_approve=None):
        SystemD.make_nginx_secrets_directory()
        if os.path.isfile(f'{secrets_dir}/server.key') and os.path.isfile(f'{secrets_dir}/server.pem'):
            if not auto_approve:
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
            if not auto_approve:
                print(f"File {secrets_dir}/dhparam.pem already exists")
                answer = input("Do you want to regenerate y/n :")
                if Helpers.check_Yes(answer):
                    run_shell_command(f"sudo openssl dhparam -out {secrets_dir}/dhparam.pem  4096", shell=True)
        else:
            print("Generating a dhparam.pem file")
            run_shell_command(f"sudo openssl dhparam -out {secrets_dir}/dhparam.pem  4096", shell=True)

    @staticmethod
    def setup_nginx_password(secrets_dir, usertype, username):
        run_shell_command(f'sudo mkdir -p {secrets_dir}', shell=True)
        print('-----------------------------')
        print(f'Setting up nginx password for user of type {usertype}')
        run_shell_command(f'sudo touch {secrets_dir}/htpasswd.{usertype}', fail_on_error=True, shell=True)
        run_shell_command(f'sudo htpasswd -c {secrets_dir}/htpasswd.{usertype} {username}', shell=True)
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
            sys.exit()
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
        return

    @staticmethod
    def parse_config_from_args(args):
        settings = SystemDSettings()
        settings.trusted_node = args.trustednode
        settings.host_ip = args.hostip
        settings.enable_transaction = args.enabletransactions
        settings.data_directory = args.data_directory
        if args.network in ["s", "S", "stokenet"]:
            settings.network_id = 2
        elif args.network in ["m", "M", "mainnet"]:
            settings.network_id = 1
        else:
            print("Pleese enter s or m for stokenet or mainnet.")
            sys.exit()
        if not args.release:
            settings.core_release = latest_release()
        else:
            settings.core_release = args.release

        if not args.nginxrelease:
            settings.nginx_release = latest_release("radixdlt/radixdlt-nginx")
        else:
            settings.nginx_release = args.nginxrelease

        settings.node_binary_url = os.getenv(NODE_BINARY_OVERIDE,
                                             f"https://github.com/radixdlt/radixdlt/releases/download/{settings.core_release}/radixdlt-dist-{settings.core_release}.zip")

        settings.nginx_config_url = os.getenv(NGINX_BINARY_OVERIDE,
                                              f"https://github.com/radixdlt/radixdlt-nginx/releases/download/{settings.nginx_release}/radixdlt-nginx-{settings.node_type}-conf.zip")

        settings.node_version = settings.node_binary_url.rsplit('/', 2)[-2]
        return settings

    @staticmethod
    def save_settings(settings):
        with open('systemd.settings.yml', 'w') as f:
            yaml.dump(settings, f, sort_keys=False, default_flow_style=False)

    @staticmethod
    def load_settings():
        if not os.path.isfile(f'systemd.settings.yml'):
            print(f"No configuration found. Execute 'radixnode systemd config' first.")
            sys.exit()
        with open('systemd.settings.yml', 'r') as f:
            settings = yaml.load(f, Loader=UnsafeLoader)
        return settings
