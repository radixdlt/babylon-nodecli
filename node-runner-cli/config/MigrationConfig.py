from config.BaseConfig import BaseConfig
from utils.Prompts import Prompts


class CommonMigrationSettings(BaseConfig):
    use_olympia: bool = False
    olympia_node_url: str = ""
    olympia_node_auth_user: str = ""
    olympia_node_auth_password: str = ""
    olympia_node_bech32_address: str = ""

    def ask_migration_config(self, olympia_node_url, olympia_node_auth_user, olympia_node_auth_password,
                             olympia_node_bech32_address):
        self.use_olympia = True

        if olympia_node_url is None:
            olympia_node_url = Prompts.ask_olympia_node_url()
        self.olympia_node_url = olympia_node_url

        if olympia_node_bech32_address is None:
            olympia_node_bech32_address = Prompts.ask_olympia_node_bech32_address()
        self.olympia_node_bech32_address = olympia_node_bech32_address

        if olympia_node_auth_user is None:
            olympia_node_auth_user = Prompts.ask_olympia_node_auth_user()
        self.olympia_node_auth_user = olympia_node_auth_user

        if olympia_node_auth_password is None:
            olympia_node_auth_password = Prompts.ask_olympia_node_auth_password()
        self.olympia_node_auth_password = olympia_node_auth_password


