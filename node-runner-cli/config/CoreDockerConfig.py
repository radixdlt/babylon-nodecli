import os
from pathlib import Path

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import CORE_DOCKER_REPO_OVERRIDE, MOUNT_LEDGER_VOLUME
from config.KeyDetails import KeyDetails
from setup.BaseSetup import BaseSetup
from utils.Prompts import Prompts
from utils.utils import Helpers
from log_util.logger import get_logger
logger = get_logger(__name__)


class CoreDockerConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.nodetype: str = "fullnode"
        self.composefileurl: str = ""
        self.keydetails: KeyDetails = KeyDetails(config_dict.get("keydetails"))
        self.core_release: str = ""
        self.repo: str = os.getenv(CORE_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-node")
        self.data_directory: str = f"{Helpers.get_home_dir()}/babylon-ledger"
        self.trusted_node: str = ""
        self.memory_limit: str = "14000m"
        self.validator_address: str = ""
        self.java_opts: str = "--enable-preview -server -Xms12g -Xmx12g  " \
                              "-XX:MaxDirectMemorySize=2048m " \
                              "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops " \
                              "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts " \
                              "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom " \
                              "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"
        super().__init__(config_dict)

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
            logger.info(f"Creating directory: {self.data_directory}")
            Path(self.data_directory).mkdir(parents=True, exist_ok=True)

    def set_trusted_node(self, trusted_node):
        if not trusted_node:
            trusted_node = Prompts.ask_trusted_node()
        self.trusted_node = trusted_node

    def ask_config(self, release, trustednode, ks_password, new_keystore, validator):

        self.set_core_release(release)
        self.set_trusted_node(trustednode)
        self.ask_validator_address(validator)
        self.keydetails = BaseSetup.ask_keydetails(ks_password, new_keystore)
        self.ask_data_directory()
        return self

    def set_validator_address(self, validator_address: str):
        self.validator_address = validator_address

    def ask_validator_address(self, validator_address=None):
        if validator_address is None:
            validator_address = Prompts.ask_validator_address()
        self.set_validator_address(validator_address)
