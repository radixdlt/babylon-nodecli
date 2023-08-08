from config.BaseConfig import BaseConfig
from utils.Prompts import Prompts


class CoreApiNodeConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.Name = "Core"
        self.core_api_address = "http://core:3333"
        self.trust_weighting = 1
        self.request_weighting = 1
        self.enabled = "true"
        self.basic_auth_user = ""
        self.basic_auth_password = ""
        self.auth_header = ""
        self.disable_core_api_https_certificate_checks: str = ""
        super().__init__(config_dict)

    def ask_disablehttpsVerify(self):
        self.disable_core_api_https_certificate_checks = Prompts.get_disablehttpsVerfiy()
