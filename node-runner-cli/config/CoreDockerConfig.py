import os
from pathlib import Path

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import CORE_DOCKER_REPO_OVERRIDE, MOUNT_LEDGER_VOLUME
from config.KeyDetails import KeyDetails
from setup.BaseSetup import BaseSetup
from utils.Prompts import Prompts
from utils.utils import Helpers


class CoreDockerConfig(BaseConfig):
    nodetype: str = "fullnode"
    composefileurl: str = None
    keydetails: KeyDetails = KeyDetails({})
    core_release: str = None
    repo: str = os.getenv(CORE_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-node")
    data_directory: str = f"{Helpers.get_home_dir()}/babylon-ledger"
    enable_transaction: str = "false"
    trusted_node: str = None
    validator_address: str = None
    java_opts: str = "--enable-preview -server -Xms8g -Xmx8g  " \
                     "-XX:MaxDirectMemorySize=2048m " \
                     "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops " \
                     "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts " \
                     "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom " \
                     "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"

    def __init__(self, settings: dict):
        super().__init__(settings)

    def set_node_type(self, nodetype="fullnode"):
        self.nodetype = nodetype

    def set_core_release(self, release):
        self.core_release = release
        # Using hardcoded tag value till we publish keygen image
        self.keydetails.keygen_tag = "v1.4.1"

    def ask_data_directory(self):
        if "DETAILED" in SetupMode.instance().mode:
            self.data_directory = BaseSetup.get_data_dir(create_dir=False)
        if os.environ.get(MOUNT_LEDGER_VOLUME, "true").lower() == "false":
            self.data_directory = None
        if self.data_directory:
            Path(self.data_directory).mkdir(parents=True, exist_ok=True)

    def ask_enable_transaction(self):
        if "DETAILED" in SetupMode.instance().mode:
            self.enable_transaction = Prompts.ask_enable_transaction()
        elif "GATEWAY" in SetupMode.instance().mode:
            self.enable_transaction = "true"

    def set_trusted_node(self, trusted_node):
        if not trusted_node:
            trusted_node = Prompts.ask_trusted_node()
        self.trusted_node = trusted_node

    def create_config(self, release, trustednode, ks_password, new_keystore, validator):

        self.set_core_release(release)
        self.set_trusted_node(trustednode)
        self.ask_validator_address(validator)
        self.keydetails = BaseSetup.ask_keydetails(ks_password, new_keystore)
        self.ask_data_directory()
        self.ask_enable_transaction()
        return self

    def set_validator_address(self, validator_address: str):
        self.validator_address = validator_address

    def ask_validator_address(self, validator_address=None):
        if validator_address is None:
            validator_address = Prompts.ask_validator_address()
        self.set_validator_address(validator_address)
