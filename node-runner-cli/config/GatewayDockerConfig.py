import os

from config.BaseConfig import BaseConfig, SetupMode
from config.EnvVars import GATEWAY_DOCKER_REPO_OVERRIDE, AGGREGATOR_DOCKER_REPO_OVERRIDE, MIGRATION_DOCKER_REPO_OVERRIDE
from utils.Prompts import Prompts
from utils.utils import Helpers


class PostGresConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.user: str = "postgres"
        self.password: str = ""
        self.dbname: str = "radixdlt_ledger"
        self.setup: str = "local"
        self.host: str = "host.docker.internal:5432"
        super().__init__(config_dict)

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
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.Name = "Core"
        self.core_api_address = "http://core:3333"
        self.trust_weighting = 1
        self.request_weighting = 1
        self.enabled = "true"
        self.basic_auth_user = ""
        self.basic_auth_password = ""
        self.auth_header = ""
        self.disable_core_api_https_certificate_checks: str = ""
        super().__init__(config_dict)

    def ask_disablehttpsVerify(self):
        self.disable_core_api_https_certificate_checks = Prompts.get_disablehttpsVerfiy()


class DatabaseMigrationConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.release: str = ""
        self.repo: str = os.getenv(MIGRATION_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-database-migrations")
        super().__init__(config_dict)


class DataAggregatorConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.release: str = ""
        self.repo: str = os.getenv(AGGREGATOR_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-data-aggregator")
        self.restart: str = "unless-stopped"
        self.NetworkName: str = ""
        self.coreApiNode: CoreApiNodeConfig = CoreApiNodeConfig(config_dict.get("coreApiNode"))
        super().__init__(config_dict)


class GatewayAPIDockerConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.release: str = ""
        self.repo: str = os.getenv(GATEWAY_DOCKER_REPO_OVERRIDE, "radixdlt/babylon-ng-gateway-api")
        self.coreApiNode: CoreApiNodeConfig = CoreApiNodeConfig(config_dict.get("coreApiNode"))
        self.restart = "unless-stopped"
        self.enable_swagger = "true"
        self.max_page_size = "30"
        super().__init__(config_dict)


class GatewayDockerConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.data_aggregator: DataAggregatorConfig = DataAggregatorConfig(config_dict.get("data_aggregator"))
        self.gateway_api: GatewayAPIDockerConfig = GatewayAPIDockerConfig(config_dict.get("gateway_api"))
        self.postgres_db: PostGresConfig = PostGresConfig(config_dict.get("postgres_db"))
        self.database_migration: DatabaseMigrationConfig = DatabaseMigrationConfig(
            config_dict.get("database_migration"))
        self.enabled: bool = False
        self.docker_compose: str = f"{Helpers.get_home_dir()}/gateway.docker-compose.yml"
