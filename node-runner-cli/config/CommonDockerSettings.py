import json

from config.BaseConfig import BaseConfig, SetupMode
from config.Nginx import DockerNginxConfig
from github import github
from utils.Network import Network
from utils.Prompts import Prompts, Helpers


class NginxConfig(BaseConfig):
    # uncomment below when support to gateway is added
    # protect_gateway: str = "true"
    # gateway_behind_auth: str = "true"
    enable_transaction_api = "false"
    protect_core: str = "true"
    release = None
    repo = "radixdlt/babylon-nginx"


class CommonDockerSettings(BaseConfig):
    network_id: int = None
    network_name: str = None
    genesis_bin_data_file: str = None
    nginx_settings: DockerNginxConfig = DockerNginxConfig({})
    docker_compose: str = f"{Helpers.get_home_dir()}/docker-compose.yml"

    def __init__(self, settings: dict):
        super().__init__(settings)
        for key, value in settings.items():
            setattr(self, key, value)

        if self.network_id:
            self.set_network_name()
        self.nginx_settings = DockerNginxConfig({})

    def __iter__(self):
        class_variables = {key: value
                           for key, value in self.__class__.__dict__.items()
                           if not key.startswith('__') and not callable(value)}
        for attr, value in class_variables.items():
            if attr in ['nginx_settings'] and self.__getattribute__(attr):
                yield attr, dict(self.__getattribute__(attr))
            elif self.__getattribute__(attr):
                yield attr, self.__getattribute__(attr)

    def set_network_id(self, network_id: int):
        self.network_id = network_id
        self.set_network_name()

    def set_genesis_bin_data_file_location(self, genesis_bin_data_file: str):
        self.genesis_bin_data_file = genesis_bin_data_file

    def set_genesis_type(self, genesis_file_location: str):
        if genesis_file_location is None:
            self.genesis_type = "json"
        elif genesis_file_location.endswith('.json'):
            self.genesis_type = "json"
        elif genesis_file_location.endswith('.bin'):
            self.genesis_type = "binary"
        else:
            self.genesis_type = "json"

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
