from config.BaseConfig import BaseConfig
from config.CommonDockerConfig import CommonDockerConfig
from config.CoreDockerConfig import CoreDockerConfig
from config.GatewayDockerConfig import GatewayDockerConfig
from config.MigrationConfig import CommonMigrationConfig


class DockerConfig(BaseConfig):

    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.core_node: CoreDockerConfig = CoreDockerConfig(config_dict.get("core_node"))
        self.common_config: CommonDockerConfig = CommonDockerConfig(config_dict.get("common_config"))
        self.gateway: GatewayDockerConfig = GatewayDockerConfig(config_dict.get("gateway"))
        self.migration: CommonMigrationConfig = CommonMigrationConfig(config_dict.get("migration"))
        super().__init__(config_dict)
