import getpass
import os
import sys
from pathlib import Path

import yaml

from config.BaseConfig import SetupMode
from config.KeyDetails import KeyDetails
from log_util.logger import get_logger
from setup.AnsibleRunner import AnsibleRunner
from utils.PromptFeeder import QuestionKeys
from utils.Prompts import Prompts
from utils.utils import run_shell_command, Helpers, bcolors, is_sudo_installed

logger = get_logger(__name__)


class BaseSetup:
    @staticmethod
    def dependencies(install_docker=True):
        if is_sudo_installed():
            if install_docker:
                logger.info("Installing docker")
                run_shell_command(
                    "curl -fsSL https://get.docker.com -o get-docker.sh", shell=True
                )
                run_shell_command("sudo sh get-docker.sh", shell=True)
                BaseSetup.add_user_docker_group()
                logger.info("Docker successfully installed")
            run_shell_command(
                "sudo apt install -y wget unzip rng-tools ansible", shell=True
            )
            run_shell_command("sudo rngd -r /dev/random | true", shell=True)
            try:
                ansible_dir = f"https://raw.githubusercontent.com/radixdlt/babylon-nodecli/{Helpers.cli_version()}/node-runner-cli"
                AnsibleRunner(ansible_dir).check_install_ansible(False)
            except Exception as e:
                logger.error(f"An error occurred while installing ansible: {e}")
        else:
            logger.info(
                "sudo is not installed in the system. You need sudo to install dependencies"
            )
            sys.exit(99)

    @staticmethod
    def add_user_docker_group():
        run_shell_command("sudo groupadd docker", shell=True, fail_on_error=False)
        is_in_docker_group = run_shell_command(
            "groups | grep docker", shell=True, fail_on_error=False
        )
        if is_in_docker_group.returncode != 0:
            run_shell_command(
                f"sudo usermod -aG docker {os.environ.get('USER')}", shell=True
            )
            print(
                'Exit ssh login and relogin back for user addition to group "docker" to take effect'
            )

    @staticmethod
    def add_radixdlt_user_docker_group():
        run_shell_command("sudo groupadd docker", shell=True, fail_on_error=False)
        is_in_docker_group = run_shell_command(
            "groups | grep docker", shell=True, fail_on_error=False
        )
        if is_in_docker_group.returncode != 0:
            run_shell_command(f"sudo usermod -aG docker radixdlt", shell=True)
            print(
                'Exit ssh login and relogin back for user addition to group "docker" to take effect'
            )

    @staticmethod
    def fetch_universe_json(trustenode, extraction_path="."):
        run_shell_command(
            f"sudo wget --no-check-certificate -O {extraction_path}/universe.json https://{trustenode}/universe.json",
            shell=True,
        )

    @staticmethod
    def get_key_details(
        keyfile_path, keyfile_name, keygen_tag, keystore_password=None, new=False
    ):
        key_details = KeyDetails({})
        key_details.keyfile_name = keyfile_name
        key_details.keygen_tag = keygen_tag
        key_details.keyfile_path = keyfile_path
        Path(f"{key_details.keyfile_path}").mkdir(parents=True, exist_ok=True)
        if os.path.isfile(f"{key_details.keyfile_path}/{key_details.keyfile_name}"):
            print(
                f"Node Keystore file already exist at location {key_details.keyfile_path}"
            )
            key_details.keystore_password = (
                keystore_password
                if keystore_password
                else getpass.getpass(
                    f"Enter the password of the existing keystore file '{key_details.keyfile_name}':"
                )
            )
        else:
            if not new:
                ask_keystore_exists = input(
                    f"Do you have keystore file named '{key_details.keyfile_name}' already from previous node Y/n?:"
                )
                if Helpers.check_Yes(ask_keystore_exists):
                    print(
                        f"\nCopy the keystore file '{key_details.keyfile_name}' to the location {key_details.keyfile_path} and then rerun the command"
                    )
                    sys.exit(1)

            print(
                f"""
            \nGenerating new keystore file. Don't forget to backup the key from location {key_details.keyfile_path}/{key_details.keyfile_name}
            """
            )
            key_details.keystore_password = (
                keystore_password
                if keystore_password
                else getpass.getpass(
                    f"Enter the password of the new file '{key_details.keyfile_name}':"
                )
            )
        return key_details

    @staticmethod
    def ask_keydetails(ks_password=None, new_keystore=False, ks_file=None):
        keydetails = KeyDetails({})
        if "DETAILED" in SetupMode.instance().mode:
            if ks_file is None:
                keydetails.keyfile_path = Prompts.ask_keyfile_path()
            else:
                keydetails.keyfile_path = ks_file
            keydetails.keyfile_name = Prompts.ask_keyfile_name()

        keydetails = BaseSetup.get_key_details(
            keyfile_path=keydetails.keyfile_path,
            keyfile_name=keydetails.keyfile_name,
            keygen_tag=keydetails.keygen_tag,
            keystore_password=ks_password,
            new=new_keystore,
        )
        return keydetails

    @staticmethod
    def ask_engine_state_api(auto_approve: bool):
        return Prompts.ask_engine_state_api(auto_approve)

    @staticmethod
    def setup_node_optimisation_config(
        version, setup_ulimit: bool, setup_swap_space_argument: bool, swap_space: str
    ):
        ansibleRunner = AnsibleRunner(
            f"https://raw.githubusercontent.com/radixdlt/babylon-nodecli/{version}/node-runner-cli"
        )
        file = "ansible/project/provision.yml"
        ansibleRunner.check_install_ansible()
        ansibleRunner.download_ansible_file(file)
        ansibleRunner.install_ansible_modules()
        if setup_ulimit is None:
            setup_limits = Prompts.ask_ansible_setup_limits()
        else:
            setup_limits = setup_ulimit

        if setup_limits:
            ansibleRunner.run_setup_limits(setup_limits)

        if setup_swap_space_argument is None:
            setup_swap, ask_swap_size = Prompts.ask_ansible_swap_setup()
        else:
            setup_swap = setup_swap_space_argument
            ask_swap_size = swap_space

        if setup_swap:
            ansibleRunner.run_swap_size(setup_swap, ask_swap_size)

    @staticmethod
    def get_data_dir(create_dir=True):
        Helpers.section_headline("LEDGER LOCATION")
        data_dir_path = Helpers.input_guestion(
            f"\nRadix node stores all the ledger data on a folder. "
            f"Mounting this location as a docker volume, "
            f"will allow to restart the node without a need to download the ledger."
            f'\n{bcolors.WARNING}Press Enter to store ledger in the "{Helpers.get_home_dir()}/babylon-ledger" directory OR '
            f"type the absolute path of an existing ledger data folder:{bcolors.ENDC}",
            QuestionKeys.input_ledger_path,
        )
        if data_dir_path == "":
            data_dir_path = f"{Helpers.get_home_dir()}/babylon-ledger"
        if create_dir:
            run_shell_command(f"sudo mkdir -p {data_dir_path}", shell=True)
        return data_dir_path

    @staticmethod
    def get_download_community_snapshot():
        Helpers.section_headline("DOWNLOAD COMMUNITY SNAPSHOT")
        print(f"\n Latest snapshot version of the ledger can be downloaded")
        download_community_snapshot_string = Helpers.input_guestion(
            f"\nRadix node stores all the ledger data on a folder."
            f"Downloading latest snapshot of the ledger will allow to sync faster when starting the node"
            f"if the ledger folder is empty."
            f'\n{bcolors.WARNING}Press Enter to accept default or choose to download latest snapshot of the ledger [true/false] ',
            QuestionKeys.input_ledger_path,
        )
        if download_community_snapshot_string == "":
            download_community_snapshot = True
        elif download_community_snapshot_string == "false":
            download_community_snapshot = False
        else :
             download_community_snapshot = True
        return download_community_snapshot

    @staticmethod
    def load_all_config(configfile):
        yaml.add_representer(type(None), Helpers.represent_none)

        if os.path.exists(configfile):
            with open(configfile, "r") as file:
                all_config = yaml.safe_load(file)
                return all_config
        else:
            print(f"Config file '{configfile}' doesn't exist")
            return {}
