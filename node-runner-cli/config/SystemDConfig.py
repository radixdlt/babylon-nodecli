import sys

import yaml

from config.BaseConfig import BaseConfig
from config.KeyDetails import KeyDetails
from config.Nginx import SystemdNginxConfig
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


class CommonSystemdSettings(BaseConfig):
    nginx_settings: SystemdNginxConfig = SystemdNginxConfig({})
    host_ip: str = None
    service_user: str = "radixdlt"
    node_dir: str = '/etc/radixdlt/node'
    node_secrets_dir: str = '/etc/radixdlt/node/secrets'
    node_version: str = None
    network_id: int = 1


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
    settings.core_node_settings =CoreSystemdSettings(dictionary["core_node_settings"])
    settings.core_node_settings.keydetails = KeyDetails(dictionary["core_node_settings"]["keydetails"])
    settings.common_settings.nginx_settings = SystemdNginxConfig(dictionary["common_settings"]["nginx_settings"])
    return settings


def extract_network_id_from_arg(networkid_arg) -> int:
    if networkid_arg == 1 or networkid_arg == 2:
        return networkid_arg
    elif networkid_arg in ["2", "s", "S", "stokenet"]:
        return 2
    elif networkid_arg in ["1", "m", "M", "mainnet"]:
        return 1
    print(
        "Not a valid argument for network id. Please enter either '1' 'm' 'M' 'mainnet' or '2' 's' 'S' 'stokenet'")
    sys.exit(1)
