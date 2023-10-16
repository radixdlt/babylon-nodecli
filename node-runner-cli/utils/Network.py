import os.path
import sys

from config.Genesis import GenesisConfig
from utils.PromptFeeder import QuestionKeys
from utils.utils import Helpers, run_shell_command


class Network:

    @staticmethod
    def get_network_id() -> int:
        # Network id
        Helpers.section_headline(f"Network connection")
        network_prompt = Helpers.input_guestion(
            "Enter the network_id. Enter M or 1 for mainnet and S or 2 for stokenet:",
            QuestionKeys.select_network)
        network_id = Network.validate_network_id(network_prompt)
        return network_id

    @staticmethod
    def validate_network_id(network_prompt: str) -> int:
        if network_prompt.lower() in ["s", "S", "stokenet"]:
            network_id = 2
        elif network_prompt.lower() in ["m", "M", "mainnet"]:
            network_id = 1
        elif network_prompt in Network.get_network_ids_strings():
            network_id = int(network_prompt)
        else:
            print("Input for network id is wrong. Exiting command")
            sys.exit(1)
        return network_id

    @staticmethod
    def path_to_genesis_binary(network_id: int) -> str:
        if network_id not in [1, 2] and network_id == 14:
            if os.path.exists("zabanet_genesis_data_file.bin"):
                run_shell_command('sudo rm zabanet_genesis_data_file.bin', shell=True)
            genesis_bin_file = GenesisConfig.copy_genesis_file(
                "zabanet_genesis_data_file.bin")
        else:
            genesis_bin_file = None

        return genesis_bin_file

    @staticmethod
    def get_network_id_names() -> dict:
        network_id_names = {
            1: "mainnet",
            2: "stokenet",
            14: "zabanet",
            32: "gilganet",
            33: "enkinet",
            34: "hammunet",
            35: "nerglanet",
            36: "mardunet"
        }
        return network_id_names

    @staticmethod
    def get_network_ids_strings() -> list:
        return [str(network_id) for network_id in Network.get_network_id_names().keys()]

    @staticmethod
    def get_network_name(network_id: int) -> str:
        return Network.get_network_id_names()[network_id]
