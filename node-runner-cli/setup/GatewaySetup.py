from urllib.parse import urlparse

from config.BaseConfig import SetupMode
from config.GatewayDockerConfig import GatewayDockerConfig, CoreApiNodeConfig
from config.SystemDConfig import SystemDConfig
from github import github
from setup.AnsibleRunner import AnsibleRunner
from setup.DockerCompose import DockerCompose
from utils.Prompts import Prompts
from utils.utils import Helpers


class GatewaySetup():
    @staticmethod
    def conditionally_install_local_postgreSQL(gateway_config: GatewayDockerConfig):
        if gateway_config.postgres_db.setup == 'local' and gateway_config.enabled:
            ansible_dir = f'https://raw.githubusercontent.com/radixdlt/babylon-nodecli/{Helpers.cli_version()}/node-runner-cli'
            AnsibleRunner(ansible_dir).run_setup_postgress(
                gateway_config.postgres_db.get("password"),
                gateway_config.postgres_db.get("user"),
                gateway_config.postgres_db.get("dbname"),
                'ansible/project/provision.yml')

    # This method asks for these inputs in that order:
    # Core Node Address
    # Core Node Name
    # Postgres Location
    # Postgres User
    # Postgres Password
    # Gateway Release
    # Aggregatorr Release
    # DatabaseMigration Release
    @staticmethod
    def ask_gateway_standalone_docker(postgres_password: str) -> GatewayDockerConfig:
        gateway_config: GatewayDockerConfig = GatewayDockerConfig({})
        gateway_config.enabled = True

        gateway_config.data_aggregator.coreApiNode = GatewaySetup.ask_core_api_node_settings("http://localhost:3332")
        gateway_config.gateway_api.coreApiNode = gateway_config.data_aggregator.coreApiNode

        gateway_config.gateway_api.release = GatewaySetup.ask_gateway_release("gateway_api")
        gateway_config.data_aggregator.release = GatewaySetup.ask_gateway_release("data_aggregator")
        gateway_config.database_migration.release = GatewaySetup.ask_gateway_release("database_migration")

        gateway_config.postgres_db.ask_postgress_settings(postgres_password)

        return gateway_config

    # This method asks for these inputs in that order:
    # Core Node Address
    # Core Node Name
    # Postgres Location
    # Postgres User
    # Postgres Password
    # Gateway Release
    # Aggregatorr Release
    # DatabaseMigration Release
    @staticmethod
    def ask_gateway_full_docker(postgres_password: str, url: str) -> GatewayDockerConfig:
        gateway_config: GatewayDockerConfig = GatewayDockerConfig({})
        gateway_config.enabled = True

        gateway_config.data_aggregator.coreApiNode = GatewaySetup.ask_core_api_node_settings(url)
        gateway_config.gateway_api.coreApiNode = gateway_config.data_aggregator.coreApiNode

        gateway_config.postgres_db.ask_postgress_settings(postgres_password)

        gateway_config.gateway_api.release = GatewaySetup.ask_gateway_release("gateway_api")
        gateway_config.data_aggregator.release = GatewaySetup.ask_gateway_release("data_aggregator")
        gateway_config.database_migration.release = GatewaySetup.ask_gateway_release("database_migration")

        return gateway_config

    # This method asks for these inputs in that order:
    # Core Node Address
    # Core Node Name
    @staticmethod
    def ask_core_api_node_settings(core_api_address: str):
        coreApiNode = CoreApiNodeConfig({})
        if "DETAILED" in SetupMode.instance().mode:
            coreApiNode.core_api_address = Prompts.get_CoreApiAddress(core_api_address)

            # ask basic auth
            parsed_url = urlparse(coreApiNode.core_api_address)
            if parsed_url.scheme == "https":
                auth = Prompts.ask_basic_auth()
                coreApiNode.basic_auth_password = auth["password"]
                coreApiNode.basic_auth_user = auth["name"]
                coreApiNode.auth_header = Helpers.get_basic_auth_header(auth)
                coreApiNode.ask_disablehttpsVerify()

            coreApiNode.Name = Prompts.ask_CopeAPINodeName()
        return coreApiNode

    @staticmethod
    def ask_gateway_release(component: str = "gateway_api") -> str:
        latest_gateway_release = github.latest_release("radixdlt/babylon-gateway")
        release = latest_gateway_release
        if "DETAILED" in SetupMode.instance().mode:
            release = Prompts.get_gateway_release(component, latest_gateway_release)
        return release

    @staticmethod
    def conditionaly_install_standalone_gateway(config: SystemDConfig, auto_approve: bool = False):
        if config.gateway.enabled:
            DockerCompose.install_standalone_gateway_in_docker(config, auto_approve)
