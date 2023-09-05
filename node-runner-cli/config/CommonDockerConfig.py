import json

from config.BaseConfig import BaseConfig, SetupMode
from config.Nginx import DockerNginxConfig
from github import github
from utils.Network import Network
from utils.Prompts import Prompts, Helpers


class CommonDockerConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.nginx_settings: DockerNginxConfig = DockerNginxConfig(config_dict.get("nginx_settings"))
        self.network_id: int = ""
        self.network_name: str = ""
        self.docker_compose: str = f"{Helpers.get_home_dir()}/docker-compose.yml"
        super().__init__(config_dict)
        if self.network_id:
            self.set_network_name()

    def set_network_id(self, network_id: int):
        self.network_id = network_id
        self.set_network_name()

    def set_genesis_bin_data_file_location(self, genesis_bin_data_file: str):
        if genesis_bin_data_file:
            self.genesis_bin_data_file = genesis_bin_data_file

    def set_network_name(self):
        if self.network_id:
            self.network_name = Network.get_network_name(self.network_id)
        else:
            raise ValueError("Network id is set incorrect")

    def ask_network_id(self, network_id):
        if not network_id:
            network_id = Network.get_network_id()
        self.set_network_id(int(network_id))
        self.set_genesis_bin_data_file_location(Network.path_to_genesis_binary(self.network_id))

    def ask_nginx_release(self):
        latest_nginx_release = github.latest_release("radixdlt/babylon-nginx")
        self.nginx_settings.release = latest_nginx_release
        if "DETAILED" in SetupMode.instance().mode:
            self.nginx_settings.release = Prompts.get_nginx_release(latest_nginx_release)

    def ask_enable_nginx_for_core(self, nginx_on_core):
        if nginx_on_core:
            self.nginx_settings.protect_core = nginx_on_core
        if "DETAILED" in SetupMode.instance().mode:
            self.nginx_settings.protect_core = Prompts.ask_enable_nginx(service="CORE").lower()

    def ask_enable_nginx_for_gateway(self, nginx_on_gateway):
        if nginx_on_gateway:
            self.nginx_settings.protect_gateway = nginx_on_gateway
        if "DETAILED" in SetupMode.instance().mode:
            self.nginx_settings.protect_gateway = Prompts.ask_enable_nginx(service="GATEWAY").lower()

    def check_nginx_required(self):
        # When gateway is supported add back the condition to check gateway
        if json.loads(self.nginx_settings.protect_core.lower()):
            return True
        else:
            return False

    def ask_existing_docker_compose_file(self):
        if "DETAILED" in SetupMode.instance().mode:
            self.docker_compose = Prompts.ask_existing_compose_file()
        else:
            open(self.docker_compose, mode='a').close()
