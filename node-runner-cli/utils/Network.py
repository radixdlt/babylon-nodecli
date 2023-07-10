import sys
from pathlib import Path

from config.Genesis import GenesisConfig
from utils.PromptFeeder import QuestionKeys
from utils.Prompts import Prompts
from utils.utils import Helpers, bcolors


class Network:

    @staticmethod
    def get_network_id() -> int:
        # Network id
        Helpers.section_headline(f"Network connection")
        # TODO change this for rcnet launch
        network_prompt = Helpers.input_guestion(
            "Enter the network_id. For babylon rcnet-v2 phase 1 it is 13:",
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
        if network_id not in [1, 2] and network_id == 13:
            genesis_bin_file = GenesisConfig.copy_genesis_file(
                "ansharnet_genesis_data_file.bin")
        else:
            genesis_bin_file = None

        return genesis_bin_file

    @staticmethod
    def get_network_id_names() -> dict:
        network_id_names = {
            1: "mainnet",
            2: "stokenet",
            10: "adapanet",
            11: "nebunet",
            12: "kisharnet",
            13: "ansharnet",
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
