from config.BaseConfig import BaseConfig
from utils.utils import Helpers


class KeyDetails(BaseConfig):
    keyfile_path: str = Helpers.get_default_node_config_dir()
    keyfile_name: str = "node-keystore.ks"
    keygen_tag: str = "v1.4.1"
    keystore_password: str = None

    def __repr__(self):
        return "%s (keyfile_path=%r, keyfile_name=%r, keygen_tag=%r, keystore_password=%r)" % (
            self.__class__.__name__, self.keyfile_path, self.keyfile_name, self.keygen_tag, self.keystore_password)
