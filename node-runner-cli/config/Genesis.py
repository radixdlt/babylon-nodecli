import os.path
import shutil
import sys
from os import getenv


class GenesisConfig:

    @staticmethod
    def create_genesis_file(genesis_json_location: str, genesis: str):
        if not os.path.exists(genesis_json_location):
            f = open(genesis_json_location, "w")
            filecontent = f"{{\"genesis\": \"{genesis}\"}}"
            f.write(filecontent)
            f.close()

    @staticmethod
    def copy_genesis_file(genesis_bin_data_file: str, genesis_files="testnet-genesis") -> str:
        bundle_dir = getattr(sys, '_MEIPASS', os.getcwd())
        path_to_genesis_bin_file = getenv("GENESIS_SOURCE_PATH",
                                          os.path.abspath(
                                              os.path.join(bundle_dir,
                                                           genesis_files,
                                                           genesis_bin_data_file)))
        destination_file_path = getenv("GENESIS_PATH", f"{os.getcwd()}/{genesis_bin_data_file}")
        shutil.copy(path_to_genesis_bin_file, destination_file_path)
        return destination_file_path
