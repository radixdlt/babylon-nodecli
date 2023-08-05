import os
from pathlib import Path

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import MOUNT_LEDGER_VOLUME, NODE_BINARY_OVERIDE
from config.KeyDetails import KeyDetails
from setup.Base import Base
from utils.Prompts import Prompts
from utils.utils import Helpers


class CoreSystemdConfig(BaseConfig):
    nodetype: str = "fullnode"
    keydetails: KeyDetails = KeyDetails({})
    core_release: str = None
    core_binary_url: str = None
    core_library_url: str = None
    data_directory: str = f"{Helpers.get_home_dir()}/babylon-ledger"
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
        self.keydetails.keygen_tag = "v1.4.1"

    def generate_download_urls(self):
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
