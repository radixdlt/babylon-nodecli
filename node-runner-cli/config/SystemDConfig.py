import json
import os
import sys
from pathlib import Path

import yaml

from config.BaseConfig import BaseConfig, SetupMode
from config.KeyDetails import KeyDetails
from config.Nginx import SystemdNginxConfig
from env_vars import MOUNT_LEDGER_VOLUME, NODE_BINARY_OVERIDE, NGINX_BINARY_OVERIDE
from github import github
from github.github import latest_release
from setup.Base import Base
from utils.Network import Network
from utils.Prompts import Prompts
from utils.utils import Helpers


class CoreSystemdSettings(BaseConfig):
    nodetype: str = "fullnode"
    keydetails: KeyDetails = KeyDetails({})
    core_release: str = None
    core_binary_url: str = None
    core_library_url: str = None
    data_directory: str = f"{Helpers.get_home_dir()}/data"
    enable_transaction: str = "false"
    trusted_node: str = None
    node_dir: str = '/etc/radixdlt/node'
    node_secrets_dir: str = '/etc/radixdlt/node/secrets'
    validator_address: str = None
    java_opts: str = "--enable-preview -server -Xms8g -Xmx8g  " \
                     "-XX:MaxDirectMemorySize=2048m " \
                     "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops " \
                     "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts " \
                     "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom " \
                     "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"

    def __iter__(self):
        class_variables = {key: value
                           for key, value in self.__class__.__dict__.items()
                           if not key.startswith('__') and not callable(value)}
        for attr, value in class_variables.items():
            if attr in ['keydetails']:
                yield attr, dict(self.__getattribute__(attr))
            elif self.__getattribute__(attr):
                yield attr, self.__getattribute__(attr)

    def ask_enable_transaction(self):
        if "DETAILED" in SetupMode.instance().mode:
            self.enable_transaction = Prompts.ask_enable_transaction()

    def ask_trusted_node(self, trusted_node):
        if not trusted_node:
            trusted_node = Prompts.ask_trusted_node()
        self.trusted_node = trusted_node

    def ask_data_directory(self, data_directory):
        if data_directory is not None and data_directory != "":
            self.data_directory = data_directory
        if "DETAILED" in SetupMode.instance().mode:
            self.data_directory = Base.get_data_dir(create_dir=False)
        if os.environ.get(MOUNT_LEDGER_VOLUME, "true").lower() == "false":
            self.data_directory = None
        if self.data_directory:
            Path(self.data_directory).mkdir(parents=True, exist_ok=True)

    def set_trusted_node(self, trusted_node):
        if not trusted_node:
            trusted_node = Prompts.ask_trusted_node()
        self.trusted_node = trusted_node

    def set_core_release(self, release):
        self.core_release = release
        self.keydetails.keygen_tag = "1.3.2"

    def create_config(self, release, data_directory, trustednode, ks_password, new_keystore):
        self.set_core_release(release)
        self.set_trusted_node(trustednode)
        self.keydetails = Base.ask_keydetails(ks_password, new_keystore)
        self.ask_data_directory(data_directory)
        self.core_binary_url = os.getenv(NODE_BINARY_OVERIDE,
                                         f"https://github.com/radixdlt/babylon-node/releases/download/{self.core_release}/babylon-node-{self.core_release}.zip")
        self.core_library_url = f"https://github.com/radixdlt/babylon-node/releases/download/{self.core_release}/babylon-node-rust-arch-linux-x86_64-release-{self.core_release}.zip"
        return self

    def set_validator_address(self, validator_address: str):
        self.validator_address = validator_address

    def ask_validator_address(self, validator_address=None):
        if validator_address is None:
            validator_address = Prompts.ask_validator_address()
        self.set_validator_address(validator_address)


class CommonSystemdSettings(BaseConfig):
    nginx_settings: SystemdNginxConfig = SystemdNginxConfig({})
    host_ip: str = None
    service_user: str = "radixdlt"
    network_id: int = 1
    genesis_json_location: str

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

    def set_genesis_json_location(self, genesis_json_location: str):
        self.genesis_json_location = genesis_json_location

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
        self.set_genesis_json_location(Network.path_to_genesis_json(self.network_id))

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


class SystemDSettings(BaseConfig):
    core_node: CoreSystemdSettings = CoreSystemdSettings({})
    common_config: CommonSystemdSettings = CommonSystemdSettings({})
    gateway_settings: None

    def __iter__(self):
        class_variables = {key: value
                           for key, value in self.__class__.__dict__.items()
                           if not key.startswith('__') and not callable(value)}
        for attr, value in class_variables.items():
            if attr in ['keydetails']:
                yield attr, dict(self.__getattribute__(attr))
            elif self.__getattribute__(attr):
                yield attr, self.__getattribute__(attr)

    def to_yaml(self):
        config_to_dump = dict(self)
        config_to_dump["core_node"] = dict(self.core_node)
        config_to_dump["core_node"]["keydetails"] = dict(self.core_node.keydetails)
        config_to_dump["common_config"] = dict(self.common_config)
        config_to_dump["common_config"]["nginx_settings"] = dict(self.common_config.nginx_settings)
        return yaml.dump(config_to_dump, sort_keys=True, default_flow_style=False, explicit_start=True,
                         allow_unicode=True)

    def to_file(self, config_file):
        config_to_dump = dict(self)
        config_to_dump["core_node"] = dict(self.core_node)
        config_to_dump["core_node"]["keydetails"] = dict(self.core_node.keydetails)
        config_to_dump["common_config"] = dict(self.common_config)
        config_to_dump["common_config"]["nginx_settings"] = dict(self.common_config.nginx_settings)
        with open(config_file, 'w') as f:
            yaml.dump(config_to_dump, f, sort_keys=True, default_flow_style=False)

    def parse_config_from_args(self, args):
        self.core_node.trusted_node = args.trustednode
        self.host_ip = args.hostip
        self.core_node.enable_transaction = args.enabletransactions
        self.core_node.data_directory = args.data_directory
        self.common_config.node_dir = args.configdir
        if args.configdir is not None:
            self.core_node.node_secrets_dir = f"{self.core_node.node_dir}/secrets"
        self.core_node.network_id = args.networkid

        if not args.nginxrelease:
            self.common_config.nginx_settings.release = latest_release("radixdlt/babylon-nginx")
        else:
            self.common_config.nginx_settings.release = args.nginxrelease
        self.core_node.core_binary_url = os.getenv(NODE_BINARY_OVERIDE,
                                                   f"https://github.com/radixdlt/babylon-node/releases/download/{self.core_node.core_release}/babylon-node-{self.core_node.core_release}.zip")
        self.core_node.core_library_url = f"https://github.com/radixdlt/babylon-node/releases/download/{self.core_release}/babylon-node-rust-arch-linux-x86_64-release-{self.core_release}.zip"
        self.common_config.nginx_settings.config_url = os.getenv(NGINX_BINARY_OVERIDE,
                                                                 f"https://github.com/radixdlt/babylon-nginx/releases/download/{self.common_config.nginx_settings.release}/babylon-nginx-{self.core_node.nodetype}-conf.zip")
        return self

def from_dict(dictionary: dict) -> SystemDSettings:
    settings = SystemDSettings({})
    settings.core_node = CoreSystemdSettings({})
    settings.common_config = CommonSystemdSettings({})
    settings.core_node = CoreSystemdSettings(dictionary["core_node"])
    settings.core_node.keydetails = KeyDetails(dictionary["core_node"]["keydetails"])
    settings.common_config = CommonSystemdSettings(dictionary["common_config"])
    settings.common_config.nginx_settings = SystemdNginxConfig(dictionary["common_config"]["nginx_settings"])
    return settings


def extract_network_id_from_arg(network_id_arg) -> int:
    if network_id_arg == 1 or network_id_arg == 2:
        return network_id_arg
    elif network_id_arg in ["2", "s", "S", "stokenet"]:
        return 2
    elif network_id_arg in ["1", "m", "M", "mainnet"]:
        return 1
    elif network_id_arg is None or network_id_arg == "":
        return None
    else:
        print(
            "Not a valid argument for network id. Please enter either '1' 'm' 'M' 'mainnet' or '2' 's' 'S' 'stokenet'")
        sys.exit(1)
