import os

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import GATEWAY_DOCKER_REPO_OVERRIDE, AGGREGATOR_DOCKER_REPO_OVERRIDE, MIGRATION_DOCKER_REPO_OVERRIDE
from utils.Prompts import Prompts
from utils.utils import Helpers


class PostGresSettings(BaseConfig):
    user: str = "postgres"
    password: str = None
    dbname: str = "radixdlt_ledger"
    setup: str = "local"
    host: str = "host.docker.internal:5432"

    def ask_postgress_settings(self, postgress_password):
        Helpers.section_headline("POSTGRES SETTINGS")
        if "DETAILED" in SetupMode.instance().mode:
            self.setup, self.host = Prompts.ask_postgress_location(self.host)
            self.user = Prompts.get_postgress_user()
            self.dbname = Prompts.get_postgress_dbname()
        if not postgress_password:
            self.password = Prompts.ask_postgress_password()
        else:
            self.password = postgress_password


class CoreApiNode(BaseConfig):
    Name = "Core"
    core_api_address = "http://core:3333"
    trust_weighting = 1
    request_weighting = 1
    enabled = "true"
    basic_auth_user = None
    basic_auth_password = None
    auth_header = None
    disable_core_api_https_certificate_checks: str = None

    def ask_disablehttpsVerify(self):
        self.disable_core_api_https_certificate_checks = Prompts.get_disablehttpsVerfiy()


class DatabaseMigrationSetting(BaseConfig):
    release: str = None
    repo: str = os.getenv(MIGRATION_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-database-migrations")

    def __init__(self, settings: dict):
        for key, value in settings.items():
            setattr(self, key, value)


class DataAggregatorSetting(BaseConfig):
    release: str = None
    repo: str = os.getenv(AGGREGATOR_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-data-aggregator")
    restart: str = "unless-stopped"
    NetworkName: str = None
    coreApiNode: CoreApiNode = CoreApiNode({})

    def __init__(self, settings: dict):
        for key, value in settings.items():
            setattr(self, key, value)

    def ask_core_api_node_settings(self):
        if "DETAILED" in SetupMode.instance().mode:
            self.coreApiNode.core_api_address = Prompts.get_CoreApiAddress(self.coreApiNode.core_api_address)
            self.ask_basic_auth(self.coreApiNode.core_api_address)
            self.coreApiNode.Name = Prompts.ask_CopeAPINodeName(self.coreApiNode.Name)
            self.coreApiNode = self.coreApiNode


class GatewayAPIDockerSettings(BaseConfig):
    release: str = None
    repo: str = os.getenv(GATEWAY_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-gateway-api")
    coreApiNode: CoreApiNode = CoreApiNode({})
    restart = "unless-stopped"
    enable_swagger = "true"
    max_page_size = "30"

    def set_core_api_node_setings(self, coreApiNode: CoreApiNode):
        self.coreApiNode = coreApiNode


class GatewayDockerSettings(BaseConfig):
    data_aggregator: DataAggregatorSetting = DataAggregatorSetting({})
    gateway_api: GatewayAPIDockerSettings = GatewayAPIDockerSettings({})
    postgres_db: PostGresSettings = PostGresSettings({})
    database_migration: DatabaseMigrationSetting = DatabaseMigrationSetting({})
    enabled: bool = False
    docker_compose_file: str = "~/gateway.docker-compose.yml"

    # def create_config(self, postgress_password):
    #     self.data_aggregator.ask_core_api_node_settings()
    #     self.postgres_db.ask_postgress_settings(postgress_password)
    #     self.data_aggregator.ask_gateway_release()
    #     self.database_migration.ask_gateway_release()
    #     self.gateway_api.ask_gateway_release()
    #     self.gateway_api.set_core_api_node_setings(
    #         self.data_aggregator.coreApiNode)
    #     return self
