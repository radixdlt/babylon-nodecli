from config.BaseConfig import BaseConfig
from config.CommonDockerConfig import CommonDockerConfig
from config.CoreDockerConfig import CoreDockerConfig
from config.GatewayDockerConfig import GatewayDockerConfig
from config.MigrationConfig import CommonMigrationConfig


class DockerConfig(BaseConfig):
    core_node: CoreDockerConfig = CoreDockerConfig({})
    common_config: CommonDockerConfig = CommonDockerConfig({})
    gateway: GatewayDockerConfig = GatewayDockerConfig({})
    migration: CommonMigrationConfig = CommonMigrationConfig({})

    def __init__(self, release: str):
        super().__init__({})
        self.core_node.core_release = release
