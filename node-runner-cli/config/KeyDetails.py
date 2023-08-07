from config.BaseConfig import BaseConfig
from utils.utils import Helpers


class KeyDetails(BaseConfig):
    def __init__(self, config_dict: dict):
        self.keyfile_path: str = Helpers.get_default_node_config_dir()
        self.keyfile_name: str = "node-keystore.ks"
        self.keygen_tag: str = "v1.4.1"
        self.keystore_password: str = None
        super().__init__(config_dict)

    def __repr__(self):
        return "%s (keyfile_path=%r, keyfile_name=%r, keygen_tag=%r, keystore_password=%r)" % (
            self.__class__.__name__, self.keyfile_path, self.keyfile_name, self.keygen_tag, self.keystore_password)
