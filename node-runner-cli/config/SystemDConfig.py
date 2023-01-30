import os
import sys
from pathlib import Path

import yaml

from config.BaseConfig import BaseConfig, SetupMode
from config.KeyDetails import KeyDetails
from config.Nginx import SystemdNginxConfig
from env_vars import MOUNT_LEDGER_VOLUME
from setup.Base import Base
from utils.Prompts import Prompts
from utils.utils import Helpers


class CoreSystemdSettings(BaseConfig):
    nodetype: str = "fullnode"
    keydetails: KeyDetails = KeyDetails({})
    core_release: str = None
    core_binary_url: str = None
    repo: str = "radixdlt/radixdlt-core"
    data_directory: str = f"{Helpers.get_home_dir()}/data"
    enable_transaction: str = "false"
    trusted_node: str = None
    java_opts: str = "--enable-preview -server -Xms8g -Xmx8g  " \
                     "-XX:MaxDirectMemorySize=2048m " \
                     "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops " \
                     "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts " \
                     "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom " \
                     "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"

    def ask_enable_transaction(self, enabletransactions):
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


class CommonSystemdSettings(BaseConfig):
    nginx_settings: SystemdNginxConfig = SystemdNginxConfig({})
    host_ip: str = None
    service_user: str = "radixdlt"
    node_dir: str = '/etc/radixdlt/node'
    node_secrets_dir: str = '/etc/radixdlt/node/secrets'
    network_id: int = 1

    def set_network_id(self, network_id: int):
        self.network_id = network_id
        self.set_network_name()

    def set_genesis_json_location(self, genesis_json_location: str):
        self.genesis_json_location = genesis_json_location

    def set_network_name(self):
        if self.network_id == 1:
            self.network_name = "mainnet"
        elif self.network_id == 2:
            self.network_name = "stokenet"
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
            network_id = Base.get_network_id()
        self.set_network_id(validate_network_id(network_id))
        self.set_genesis_json_location(Base.path_to_genesis_json(self.network_id))


class SystemDSettings(BaseConfig):
    core_node_settings: CoreSystemdSettings = CoreSystemdSettings({})
    common_settings: CommonSystemdSettings = CommonSystemdSettings({})
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
        config_to_dump["core_node_settings"] = dict(self.core_node_settings)
        config_to_dump["core_node_settings"]["keydetails"] = dict(self.core_node_settings.keydetails)
        config_to_dump["common_settings"] = dict(self.common_settings)
        config_to_dump["common_settings"]["nginx_settings"] = dict(self.common_settings.nginx_settings)
        return yaml.dump(config_to_dump, sort_keys=False, default_flow_style=False, explicit_start=True,
                         allow_unicode=True)

    def to_file(self, config_file):
        config_to_dump = dict(self)
        config_to_dump["core_node_settings"] = dict(self.core_node_settings)
        config_to_dump["core_node_settings"]["keydetails"] = dict(self.core_node_settings.keydetails)
        config_to_dump["common_settings"] = dict(self.common_settings)
        config_to_dump["common_settings"]["nginx_settings"] = dict(self.common_settings.nginx_settings)
        with open(config_file, 'w') as f:
            yaml.dump(config_to_dump, f, sort_keys=True, default_flow_style=False)


def from_dict(dictionary: dict) -> SystemDSettings:
    settings = SystemDSettings({})
    settings.core_node_settings = CoreSystemdSettings(dictionary["core_node_settings"])
    settings.core_node_settings.keydetails = KeyDetails(dictionary["core_node_settings"]["keydetails"])
    settings.common_settings.nginx_settings = SystemdNginxConfig(dictionary["common_settings"]["nginx_settings"])
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


def validate_network_id(network_prompt):
    if network_prompt.lower() in ["s", "S", "stokenet"]:
        network_id = 2
    elif network_prompt.lower() in ["m", "M", "mainnet"]:
        network_id = 1
    elif network_prompt in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        network_id = int(network_prompt)
    else:
        print("Input for network id is wrong. Exiting command")
        sys.exit(1)
    return network_id
