from config.BaseConfig import BaseConfig


class CommonMigrationConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.use_olympia: bool = False
        self.olympia_node_url: str = "http://localhost:3332"
        self.olympia_node_auth_user: str = "admin"
        self.olympia_node_auth_password: str = ""
        self.olympia_node_bech32_address: str = ""
        super().__init__(config_dict)
