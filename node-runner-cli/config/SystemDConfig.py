import os

from config.BaseConfig import BaseConfig
from config.CommonSystemDConfig import CommonSystemdConfig
from config.CoreSystemDConfig import CoreSystemdConfig
from config.EnvVars import NODE_BINARY_OVERIDE, NGINX_BINARY_OVERIDE, \
    APPEND_DEFAULT_CONFIG_OVERIDES
from config.GatewayDockerConfig import GatewayDockerConfig
from config.MigrationConfig import CommonMigrationConfig
from config.Renderer import Renderer
from github.github import latest_release
from utils.Network import Network
from utils.utils import run_shell_command


class SystemDConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.core_node: CoreSystemdConfig = CoreSystemdConfig(config_dict.get("core_node"))
        self.common_config: CommonSystemdConfig = CommonSystemdConfig(config_dict.get("common_config"))
        self.migration: CommonMigrationConfig = CommonMigrationConfig(config_dict.get("migration"))
        self.gateway: GatewayDockerConfig = GatewayDockerConfig(config_dict.get("gateway"))
        super().__init__(config_dict)

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
        self.render_environment() \
            .to_file(f"{self.core_node.node_secrets_dir}/environment")

    def create_environment_yaml(self):
        return self.render_environment().to_yaml()

    def render_environment(self):
        return Renderer().load_file_based_template("systemd-environment.j2") \
            .render(self.to_dict())

    def create_default_config_file(self):
        self.common_config.genesis_bin_data_file = Network.path_to_genesis_binary(self.common_config.network_id)
        Renderer().load_file_based_template("systemd-default.config.j2").render(
            self.to_dict()).to_file(f"{self.core_node.node_dir}/default.config")

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
        Renderer().load_file_based_template("systemd.service.j2").render(self.to_dict()).to_file(tmp_service)
        command = f"sudo mv {tmp_service} {service_file_path}"
        run_shell_command(command, shell=True)
