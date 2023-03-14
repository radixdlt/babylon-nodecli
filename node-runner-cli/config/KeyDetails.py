from config.BaseConfig import BaseConfig
from utils.utils import Helpers


class KeyDetails(BaseConfig):
    keyfile_path: str = Helpers.get_default_node_config_dir()
    keyfile_name: str = "node-keystore.ks"
    keygen_tag: str = None
    keystore_password: str = None

    # def __init__(self,
    #              keyfile_path=None,
    #              keyfile_name="node-keystore.ks",
    #              keygen_tag=None,
    #              keystore_password=None):
    #     self.keyfile_path = keyfile_path
    #     self.keyfile_name = keyfile_name
    #     self.keygen_tag = keygen_tag
    #     self.keystore_password = keystore_password

    def __repr__(self):
        return "%s (keyfile_path=%r, keyfile_name=%r, keygen_tag=%r, keystore_password=%r)" % (
            self.__class__.__name__, self.keyfile_path, self.keyfile_name, self.keygen_tag, self.keystore_password)
