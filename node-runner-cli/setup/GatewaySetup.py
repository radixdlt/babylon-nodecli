from config.GatewayDockerConfig import GatewayDockerSettings
from setup.AnsibleRunner import AnsibleRunner
from utils.utils import Helpers


class GatewaySetup():
    @staticmethod
    def conditionally_install_local_postgreSQL(gateway_config: GatewayDockerSettings):
        if gateway_config.postgres_db.setup == 'local' and gateway_config.enabled:
            ansible_dir = f'https://raw.githubusercontent.com/radixdlt/babylon-nodecli/{Helpers.cli_version()}/node-runner-cli'
            AnsibleRunner(ansible_dir).run_setup_postgress(
                gateway_config.postgres_db.get("password"),
                gateway_config.postgres_db.get("user"),
                gateway_config.postgres_db.get("dbname"),
                'ansible/project/provision.yml')
