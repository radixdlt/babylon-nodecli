from config.EnvVars import COMPOSE_HTTP_TIMEOUT
from config.Renderer import Renderer
from config.SystemDConfig import SystemDConfig
from setup.DockerCommandArguments import DockerInstallArguments
from utils.utils import Helpers, run_shell_command


class DockerCompose:
    @staticmethod
    def install_standalone_gateway_in_docker(systemd_config: SystemDConfig, auto_approve: bool = False):
        docker_compose_file: str = systemd_config.gateway.docker_compose
        Renderer() \
            .load_file_based_template("standalone-gateway-compose.yml.j2") \
            .render(systemd_config.to_dict()) \
            .to_file(docker_compose_file)
        if auto_approve:
            should_start = "Y"
        else:
            should_start = input("\nOkay to start the containers [Y/n]?:")
        if Helpers.check_Yes(should_start):
            DockerCompose.run_docker_compose_up(docker_compose_file)

    @staticmethod
    def stop_gateway_containers():
        docker_compose_file: str = "~/gateway.docker-compose.yml"
        DockerCompose.run_docker_compose_down(docker_compose_file)

    @staticmethod
    def restart_gateway_containers():
        docker_compose_file: str = "~/gateway.docker-compose.yml"
        DockerCompose.run_docker_compose_down(docker_compose_file)
        DockerCompose.run_docker_compose_up(docker_compose_file)

    @staticmethod
    def confirm_run_docker_compose(argument_object: DockerInstallArguments, compose_file):
        if argument_object.autoapprove:
            print("In Auto mode -  Updating the node as per above contents of docker file")
            should_start = "Y"
        else:
            should_start = input("\nOkay to start the containers [Y/n]?:")
        if Helpers.check_Yes(should_start):
            DockerCompose.run_docker_compose_up(compose_file)

    @staticmethod
    def run_docker_compose_down(composefile, removevolumes=False):
        Helpers.docker_compose_down(composefile, removevolumes)

    @staticmethod
    def run_docker_compose_up(composefile):
        docker_compose_binary = os.getenv("DOCKER_COMPOSE_LOCATION", 'docker-compose')
        result = run_shell_command([docker_compose_binary, '-f', composefile, 'up', '-d'],
                                   env={
                                       COMPOSE_HTTP_TIMEOUT: os.getenv(COMPOSE_HTTP_TIMEOUT, "200")
                                   }, fail_on_error=False)
        if result.returncode != 0:
            run_shell_command([docker_compose_binary, '-f', composefile, 'up', '-d'],
                              env={
                                  COMPOSE_HTTP_TIMEOUT: os.getenv(COMPOSE_HTTP_TIMEOUT, "200")
                              }, fail_on_error=True)
