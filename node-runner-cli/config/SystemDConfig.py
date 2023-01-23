import os
import sys
from pathlib import Path

import yaml

from config.BaseConfig import BaseConfig, SetupMode
from config.CommonDockerSettings import CommonDockerSettings
from config.GatewayDockerConfig import GatewayDockerSettings
from env_vars import MOUNT_LEDGER_VOLUME
from setup import Base
from utils.Prompts import Prompts
from utils.utils import Helpers


class KeyDetails(BaseConfig):
    keyfile_path: str = Helpers.get_default_node_config_dir()
    keyfile_name: str = "node-keystore.ks"
    keygen_tag: str = None
    keystore_password: str = None


class SystemDSettings:
    service_user: str = "radixdlt"
    data_directory: str = f"{Helpers.get_home_dir()}/data"
    host_ip: str = "radixdlt"

    node_type: str = "fullnode"
    node_dir: str = '/etc/radixdlt/node'
    # node_dir: str = '/tmp/testdir/node'
    node_secrets_dir: str = '/etc/radixdlt/node/secrets'
    # node_secrets_dir: str = '/tmp/testdir/secrets'
    node_version: str = None

    nginx_dir: str = '/etc/nginx'
    # nginx_dir: str = '/tmp/testdir/nginx'
    nginx_secrets_dir: str = '/etc/nginx/secrets'
    # nginx_secrets_dir: str = '/tmp/nginx/secrets'
    nginx_release: str = None
    nginx_binary_url: str = None

    core_release: str = None
    core_binary_url: str = "radixdlt/radixdlt-core"
    enable_transaction: str = "false"
    trusted_node: str = None
    keydetails: KeyDetails = KeyDetails({})
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
