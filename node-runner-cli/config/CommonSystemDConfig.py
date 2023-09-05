import json
import os

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import NGINX_BINARY_OVERIDE
from config.Nginx import SystemdNginxConfig
from github import github
from utils.Network import Network
from utils.Prompts import Prompts


class CommonSystemdConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.nginx_settings: SystemdNginxConfig = SystemdNginxConfig(config_dict.get("nginx_settings"))
        self.network_id: int = 1
        self.network_name: str = ""
        self.genesis_bin_data_file: str = ""
        self.host_ip: str = ""
        self.service_user: str = "radixdlt"
        super().__init__(config_dict)

    def set_network_id(self, network_id: int):
        self.network_id = network_id
        self.set_network_name()

    def set_genesis_bin_data_file(self, genesis_bin_data_file: str):
        if genesis_bin_data_file:
            self.genesis_bin_data_file = genesis_bin_data_file

    def set_network_name(self):
        if self.network_id:
            self.network_name = Network.get_network_name(self.network_id)
        else:
            raise ValueError("Network id is set incorrect")

    def ask_host_ip(self, hostip):
        if hostip is not None:
            self.host_ip = hostip
            return
        else:
            self.host_ip = Prompts.ask_host_ip()

    def ask_network_id(self, network_id):
        if not network_id:
            network_id = Network.get_network_id()
        if isinstance(network_id, str):
            self.set_network_id(int(network_id))
        else:
            self.set_network_id(network_id)
        self.set_genesis_bin_data_file(Network.path_to_genesis_binary(self.network_id))

    def ask_enable_nginx_for_core(self, nginx_on_core):
        if nginx_on_core:
            self.nginx_settings.protect_core = nginx_on_core
        if "DETAILED" in SetupMode.instance().mode:
            self.nginx_settings.protect_core = Prompts.ask_enable_nginx(service="CORE").lower()

    def check_nginx_required(self):
        if json.loads(
                self.nginx_settings.protect_core.lower()):
            return True
        else:
            return False

    def ask_nginx_release(self):
        latest_nginx_release = github.latest_release("radixdlt/babylon-nginx")
        self.nginx_settings.release = latest_nginx_release
        if "DETAILED" in SetupMode.instance().mode:
            self.nginx_settings.release = Prompts.get_nginx_release(latest_nginx_release)
        self.nginx_settings.config_url = os.getenv(NGINX_BINARY_OVERIDE,
                                                   f"https://github.com/radixdlt/babylon-nginx/releases/download/"
                                                   f"{self.nginx_settings.release}/babylon-nginx-fullnode-conf.zip")
