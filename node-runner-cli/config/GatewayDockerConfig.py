import os

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import GATEWAY_DOCKER_REPO_OVERRIDE, AGGREGATOR_DOCKER_REPO_OVERRIDE, MIGRATION_DOCKER_REPO_OVERRIDE
from utils.Prompts import Prompts
from utils.utils import Helpers


class PostGresConfig(BaseConfig):
    user: str = "postgres"
    password: str = None
    dbname: str = "radixdlt_ledger"
    setup: str = "local"
    host: str = "host.docker.internal:5432"

    def ask_postgress_settings(self, postgress_password):
        Helpers.section_headline("POSTGRES SETTINGS")
        if "DETAILED" in SetupMode.instance().mode:
            self.setup, self.host = Prompts.ask_postgress_location(self.host)
            self.dbname = Prompts.get_postgress_dbname()
            self.user = Prompts.get_postgress_user()
        if not postgress_password:
            self.password = Prompts.ask_postgress_password()
        else:
            self.password = postgress_password


class CoreApiNodeConfig(BaseConfig):
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


class DatabaseMigrationConfig(BaseConfig):
    release: str = None
    repo: str = os.getenv(MIGRATION_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-database-migrations")


class DataAggregatorConfig(BaseConfig):
    release: str = None
    repo: str = os.getenv(AGGREGATOR_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-data-aggregator")
    restart: str = "unless-stopped"
    NetworkName: str = None
    coreApiNode: CoreApiNodeConfig = CoreApiNodeConfig({})


class GatewayAPIDockerConfig(BaseConfig):
    release: str = None
    repo: str = os.getenv(GATEWAY_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-gateway-api")
    coreApiNode: CoreApiNodeConfig = CoreApiNodeConfig({})
    restart = "unless-stopped"
    enable_swagger = "true"
    max_page_size = "30"


class GatewayDockerConfig(BaseConfig):
    data_aggregator: DataAggregatorConfig = DataAggregatorConfig({})
    gateway_api: GatewayAPIDockerConfig = GatewayAPIDockerConfig({})
    postgres_db: PostGresConfig = PostGresConfig({})
    database_migration: DatabaseMigrationConfig = DatabaseMigrationConfig({})
    enabled: bool = False
    docker_compose: str = f"{Helpers.get_home_dir()}/gateway.docker-compose.yml"
