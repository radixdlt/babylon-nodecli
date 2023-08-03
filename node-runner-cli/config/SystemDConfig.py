import json
import os
from pathlib import Path

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import MOUNT_LEDGER_VOLUME, NODE_BINARY_OVERIDE, NGINX_BINARY_OVERIDE, \
    APPEND_DEFAULT_CONFIG_OVERIDES
from config.GatewayDockerConfig import GatewayDockerConfig
from config.KeyDetails import KeyDetails
from config.MigrationConfig import CommonMigrationConfig
from config.Nginx import SystemdNginxConfig
from config.Renderer import Renderer
from github import github
from github.github import latest_release
from setup.Base import Base
from utils.Network import Network
from utils.Prompts import Prompts
from utils.utils import Helpers, run_shell_command


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


class CommonSystemdConfig(BaseConfig):
    nginx_settings: SystemdNginxConfig = SystemdNginxConfig({})
    host_ip: str = None
    service_user: str = "radixdlt"
    network_id: int = 1
    genesis_bin_data_file: str

    def set_network_id(self, network_id: int):
        self.network_id = network_id
        self.set_network_name()

    def set_genesis_bin_data_file(self, genesis_bin_data_file: str):
        self.genesis_bin_data_file = genesis_bin_data_file

    def set_genesis_type(self, genesis_file_location: str):
        if genesis_file_location.endswith('.json'):
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
        self.set_genesis_bin_data_file(Network.path_to_genesis_binary(self.network_id))

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


class SystemDConfig(BaseConfig):
    migration: CommonMigrationConfig = CommonMigrationConfig({})
    core_node: CoreSystemdConfig = CoreSystemdConfig({})
    common_config: CommonSystemdConfig = CommonSystemdConfig({})
    gateway: GatewayDockerConfig = GatewayDockerConfig({})

    def parse_config_from_args(self, args):
        self.core_node.trusted_node = args.trustednode
        self.common_config.host_ip = args.hostip
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

    def create_environment_file(self):
        run_shell_command(f'mkdir -p {self.core_node.node_secrets_dir}', shell=True)
        Renderer().load_file_based_template("systemd-environment.j2") \
            .render(dict(self.core_node.keydetails)) \
            .to_file(f"{self.core_node.node_secrets_dir}/environment")

    def create_default_config_file(self):
        self.common_config.genesis_bin_data_file = Network.path_to_genesis_binary(self.common_config.network_id)
        Renderer().load_file_based_template("systemd-default.config.j2").render(
            dict(self)).to_file(f"{self.core_node.node_dir}/default.config")

        if (os.getenv(APPEND_DEFAULT_CONFIG_OVERIDES)) is not None:
            print("Add overides")
            lines = []
            while True:
                line = input()
                if line:
                    lines.append(line)
                else:
                    break
            for text in lines:
                run_shell_command(f"echo {text} >> {self.core_node.node_dir}/default.config", shell=True)

    def create_service_file(self,
                            service_file_path="/etc/systemd/system/radixdlt-node.service"):
        # This may need to be moved to jinja template
        tmp_service: str = "/tmp/radixdlt-node.service"
        Renderer().load_file_based_template("systemd.service.j2").render(dict(self)).to_file(tmp_service)
        command = f"sudo mv {tmp_service} {service_file_path}"
        run_shell_command(command, shell=True)
