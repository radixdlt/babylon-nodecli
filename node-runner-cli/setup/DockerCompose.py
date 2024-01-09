import os
import sys

from config.Renderer import Renderer
from config.SystemDConfig import SystemDConfig
from log_util.logger import get_logger
from setup.DockerCommandArguments import DockerInstallArguments
from utils.utils import Helpers, run_shell_command

logger = get_logger(__name__)


class DockerCompose:
    @staticmethod
    def install_standalone_gateway_in_docker(
        systemd_config: SystemDConfig, auto_approve: bool = False
    ):
        docker_compose_file: str = systemd_config.gateway.docker_compose
        systemd_config.gateway.data_aggregator.coreApiNode.auth_header = (
            Helpers.get_basic_auth_header_from_user_and_password(
                systemd_config.gateway.data_aggregator.coreApiNode.basic_auth_user,
                systemd_config.gateway.data_aggregator.coreApiNode.basic_auth_password,
            )
        )
        systemd_config.gateway.gateway_api.coreApiNode.auth_header = (
            Helpers.get_basic_auth_header_from_user_and_password(
                systemd_config.gateway.gateway_api.coreApiNode.basic_auth_user,
                systemd_config.gateway.gateway_api.coreApiNode.basic_auth_password,
            )
        )
        Renderer().load_file_based_template("standalone-gateway-compose.yml.j2").render(
            systemd_config.to_dict()
        ).to_file(docker_compose_file)
        if auto_approve:
            should_start = "Y"
        else:
            should_start = input("\nOkay to start the containers [Y/n]?:")
        if Helpers.check_Yes(should_start):
            DockerCompose.run_docker_compose_up(docker_compose_file)

    @staticmethod
    def stop_gateway_containers():
        docker_compose_file: str = (
            f"{Helpers.get_home_dir()}/gateway.docker-compose.yml"
        )
        if os.path.exists(docker_compose_file):
            DockerCompose.run_docker_compose_down(docker_compose_file)

    @staticmethod
    def restart_gateway_containers():
        docker_compose_file: str = (
            f"{Helpers.get_home_dir()}/gateway.docker-compose.yml"
        )
        if os.path.exists(docker_compose_file):
            DockerCompose.run_docker_compose_down(docker_compose_file)
            DockerCompose.run_docker_compose_up(docker_compose_file)

    @staticmethod
    def confirm_run_docker_compose(
        argument_object: DockerInstallArguments, compose_file
    ):
        if argument_object.autoapprove:
            print(
                "In Auto mode -  Updating the node as per above contents of docker file"
            )
            should_start = "Y"
        else:
            should_start = input("\nOkay to start the containers [Y/n]?:")
        if Helpers.check_Yes(should_start):
            DockerCompose.run_docker_compose_up(compose_file)

    @staticmethod
    def run_docker_compose_down(composefile, remove_volumes=False):
        if DockerCompose._is_docker_compose_plugin_installed():
            command = f"docker compose -f {composefile} down"
        else:
            docker_compose_binary = os.getenv(
                "DOCKER_COMPOSE_LOCATION", "docker-compose"
            )
            command = f"{docker_compose_binary} -f {composefile} down"
        if remove_volumes:
            command += " -v"
        result = run_shell_command(command, shell=True, fail_on_error=False)
        if result.returncode != 0:
            logger.info(f"Command: {command} failed.")
            sys.exit(1)

    @staticmethod
    def run_docker_compose_up(composefile):
        if DockerCompose._is_docker_compose_plugin_installed():
            logger.info("Using the docker compose plugin to start the environment")
            command = f"docker compose -f {composefile} up -d"
        else:
            docker_compose_binary = os.getenv(
                "DOCKER_COMPOSE_LOCATION", "docker-compose"
            )
            command = f"{docker_compose_binary} -f {composefile} up -d"

        result = run_shell_command(command, shell=True)
        if result.returncode != 0:
            logger.info(f"Command: {command} failed.")
            sys.exit(1)

    @staticmethod
    def _is_docker_compose_plugin_installed():
        result = run_shell_command(
            "docker compose version", shell=True, fail_on_error=False
        )
        return result.returncode == 0
