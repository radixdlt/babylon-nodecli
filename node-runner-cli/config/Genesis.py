import os.path


class GenesisConfig:

    @staticmethod
    def create_genesis_file(genesis_json_location: str, genesis: str):
        if not os.path.exists(genesis_json_location):
            f = open(genesis_json_location, "w")
            filecontent = f"{{\"genesis\": \"{genesis}\"}}"
            f.write(filecontent)
            f.close()
