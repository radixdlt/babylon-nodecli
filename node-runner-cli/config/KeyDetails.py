from config.BaseConfig import BaseConfig
from utils.utils import Helpers


class KeyDetails(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.keyfile_path: str = Helpers.get_default_node_config_dir()
        self.keyfile_name: str = "node-keystore.ks"
        self.keygen_tag: str = "v1.4.1"
        self.keystore_password: str = ""
        super().__init__(config_dict)
