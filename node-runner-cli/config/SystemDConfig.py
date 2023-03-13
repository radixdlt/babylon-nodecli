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
    data_directory: str = f"{Helpers.get_home_dir()}/data"
    enable_transaction: str = "false"
    trusted_node: str = None
    node_dir: str = '/etc/radixdlt/node'
    node_secrets_dir: str = '/etc/radixdlt/node/secrets'
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

    def ask_keydetails(self, ks_password=None, new_keystore=False):
        keydetails = self.keydetails
        if "DETAILED" in SetupMode.instance().mode:
            keydetails.keyfile_path = Prompts.ask_keyfile_path()
            keydetails.keyfile_name = Prompts.ask_keyfile_name()

        keystore_password, file_location = Base.generatekey(
            keyfile_path=keydetails.keyfile_path,
            keyfile_name=keydetails.keyfile_name,
            keygen_tag=keydetails.keygen_tag, ks_password=ks_password, new=new_keystore)
        keydetails.keystore_password = keystore_password
        self.keydetails = keydetails

    def set_trusted_node(self, trusted_node):
        if not trusted_node:
            trusted_node = Prompts.ask_trusted_node()
        self.trusted_node = trusted_node

    def set_core_release(self, release):
        self.core_release = release
        self.keydetails.keygen_tag = self.core_release

    def create_config(self, release, data_directory, trustednode, ks_password, new_keystore):
        self.set_core_release(release)
        self.set_trusted_node(trustednode)
        self.ask_keydetails(ks_password, new_keystore)
        self.ask_data_directory(data_directory)
        self.core_binary_url = os.getenv(NODE_BINARY_OVERIDE,
                                         f"https://github.com/radixdlt/radixdlt/releases/download/{self.core_release}/radixdlt-dist-{self.core_release}.zip")
        self.node_version = self.core_binary_url.rsplit('/', 2)[-2]
        return self


class CommonSystemdSettings(BaseConfig):
    nginx_settings: SystemdNginxConfig = SystemdNginxConfig({})
    host_ip: str = None
    service_user: str = "radixdlt"
    network_id: int = 1

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
        latest_nginx_release = github.latest_release("radixdlt/radixdlt-nginx")
        self.nginx_settings.release = latest_nginx_release
        if "DETAILED" in SetupMode.instance().mode:
            self.nginx_settings.release = Prompts.get_nginx_release(latest_nginx_release)
        self.nginx_settings.config_url = os.getenv(NGINX_BINARY_OVERIDE,
                                                   f"https://github.com/radixdlt/radixdlt-nginx/releases/download/"
                                                   f"{self.nginx_settings.release}/radixdlt-nginx-fullnode-conf.zip")


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

    def parse_config_from_args(self, args):
        self.core_node_settings.trusted_node = args.trustednode
        self.host_ip = args.hostip
        self.core_node_settings.enable_transaction = args.enabletransactions
        self.core_node_settings.data_directory = args.data_directory
        self.common_settings.node_dir = args.configdir
        if args.configdir is not None:
            self.core_node_settings.node_secrets_dir = f"{self.core_node_settings.node_dir}/secrets"
        self.core_node_settings.network_id = args.networkid

        if not args.nginxrelease:
            self.common_settings.nginx_settings.release = latest_release("radixdlt/radixdlt-nginx")
        else:
            self.common_settings.nginx_settings.release = args.nginxrelease
        self.core_node_settings.core_binary_url = os.getenv(NODE_BINARY_OVERIDE,
                                                            f"https://github.com/radixdlt/radixdlt/releases/download/{self.core_node_settings.core_release}/radixdlt-dist-{self.core_node_settings.core_release}.zip")
        self.common_settings.nginx_settings.config_url = os.getenv(NGINX_BINARY_OVERIDE,
                                                                   f"https://github.com/radixdlt/radixdlt-nginx/releases/download/{self.common_settings.nginx_settings.release}/radixdlt-nginx-{self.core_node_settings.nodetype}-conf.zip")
        self.node_version = self.core_node_settings.core_binary_url.rsplit('/', 2)[-2]
        return self


def from_dict(dictionary: dict) -> SystemDSettings:
    settings = SystemDSettings({})
    settings.core_node_settings = CoreSystemdSettings(dictionary["core_node_settings"])
    settings.core_node_settings.keydetails = KeyDetails(dictionary["core_node_settings"]["keydetails"])
    settings.common_settings = CommonSystemdSettings(dictionary["common_settings"])
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
