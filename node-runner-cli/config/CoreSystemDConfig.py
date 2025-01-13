import os
from pathlib import Path

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import MOUNT_LEDGER_VOLUME, NODE_BINARY_OVERIDE
from config.KeyDetails import KeyDetails
from github.github import latest_release
from setup.BaseSetup import BaseSetup
from utils.Prompts import Prompts
from utils.utils import Helpers


class CoreSystemdConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.keydetails: KeyDetails = KeyDetails(config_dict.get("keydetails"))
        self.nodetype: str = "fullnode"
        self.core_release: str = ""
        self.core_binary_url: str = ""
        self.core_library_url: str = ""
        self.data_directory: str = f"{Helpers.get_default_ledger_dir()}"
        self.trusted_node: str = ""
        self.node_dir: str = "/etc/radixdlt/node"
        self.node_secrets_dir: str = "/etc/radixdlt/node/secrets"
        self.validator_address: str = ""
        self.engine_state_enabled: bool = False
        self.core_api_port: str = "3333"
        self.system_api_port: str = "3334"
        self.engine_state_api_port: str = "3336"
        self.engine_state_api_address: str = "0.0.0.0"
        self.java_opts: str = (
            "--enable-preview -server -Xms12g -Xmx12g  "
            "-XX:MaxDirectMemorySize=2048m "
            "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops "
            "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts "
            "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom "
            "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"
        )
        super().__init__(config_dict)

    def ask_trusted_node(self, trusted_node):
        if not trusted_node:
            trusted_node = Prompts.ask_trusted_node()
        self.trusted_node = trusted_node

    def ask_data_directory(self, data_directory):
        if data_directory is not None and data_directory != "":
            self.data_directory = data_directory
        if "DETAILED" in SetupMode.instance().mode:
            self.data_directory = BaseSetup.get_data_dir(create_dir=False)
        if os.environ.get(MOUNT_LEDGER_VOLUME, "true").lower() == "false":
            self.data_directory = None
        if self.data_directory:
            Path(self.data_directory).mkdir(parents=True, exist_ok=True)

    def set_trusted_node(self, trusted_node):
        if not trusted_node:
            trusted_node = Prompts.ask_trusted_node()
        self.trusted_node = trusted_node

    def set_core_release(self, release):
        if not release:
            release = latest_release()
        self.core_release = release
        self.keydetails.keygen_tag = "v1.4.1"

    def generate_download_urls(self):
        self.core_binary_url = os.getenv(
            NODE_BINARY_OVERIDE,
            f"https://github.com/radixdlt/babylon-node/releases/download/{self.core_release}/babylon-node-{self.core_release}.zip",
        )
        self.core_library_url = f"https://github.com/radixdlt/babylon-node/releases/download/{self.core_release}/babylon-node-rust-arch-linux-x86_64-release-{self.core_release}.zip"
        return self

    def set_validator_address(self, validator_address: str):
        self.validator_address = validator_address

    def ask_validator_address(self, validator_address=None):
        if validator_address is None:
            validator_address = Prompts.ask_validator_address()
        self.set_validator_address(validator_address)
