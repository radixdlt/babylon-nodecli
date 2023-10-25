import os.path
import sys
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pathlib import Path

from commands.subcommand import get_decorator, argument
from config.DockerConfig import DockerConfig
from log_util.logger import get_logger
from setup.BaseSetup import BaseSetup
from setup.DockerCommandArguments import DockerInstallArguments, DockerConfigArguments
from setup.DockerCompose import DockerCompose
from setup.DockerSetup import DockerSetup
from utils.utils import Helpers, bcolors

logger = get_logger(__name__)

dockercli = ArgumentParser(
    description='Subcommand to help setup CORE or GATEWAY using Docker containers',
    usage="babylonnode docker ",
    formatter_class=RawTextHelpFormatter)
docker_parser = dockercli.add_subparsers(dest="dockercommand")


def dockercommand(dockercommand_args=[], parent=docker_parser):
    return get_decorator(dockercommand_args, parent)


@dockercommand([
    argument("-a", "--autoapprove", help="Set this to true to run without any prompts and in mode CORE or GATEWAY."
                                         "Prompts still appear if you run in DETAILED mode "
                                         "Use this for automation purpose only", action="store_true", default=False),
    argument("-d", "--configdir",
             help=f"Path to node-config directory where config file will stored. Default value is {Helpers.get_default_node_config_dir()}",
             action="store",
             default=f"{Helpers.get_default_node_config_dir()}"),
    argument("-k", "--keystorepassword",
             help=f"""Core Node requires a keystore. This is the password for the keystore file
                    the CLI will create new key with name `node-keystore.ks` in config directory.
                     If the keystore exists in config directory, CLI finds it , and uses the password from -k parameter 
                     or prompt for the password to be entered. CLI never modifies the password of keystore
             """,
             action="store",
             default=""),
    argument("-m", "--setupmode", nargs="+",
             required=True,
             help="""Quick config mode with assumed defaults. It supports two quick modes and a detailed config mode.
                  \n\nCORE: Use this value to setup CORE using defaults.
                  \n\nGATEWAY: Use this value to setup GATEWAY using defaults.
                  \n\nDETAILED: Default value if not provided. This mode takes your through series of questions.
                  """,
             choices=["CORE", "GATEWAY", "DETAILED", "MIGRATION"], action="store"),
    argument("-miu", "--migration_url",
             help="The root url of the olympia node to migrate the ledger from. Do not add /olympia-end-state.",
             action="store"),
    argument("-miau", "--migration_auth_user", help="The user to authenticate to the olympia node for migration",
             action="store"),
    argument("-miap", "--migration_auth_password",
             help="The password to authenticate to the olympia node for migration", action="store"),
    argument("-miba", "--migration_bech_address",
             help="The bech address of the olympia node to migrate the ledger from",
             action="store"),
    argument("-n", "--networkid",
             help="Network id of network you want to connect.For stokenet it is 2 and for mainnet it is 1."
                  "If not provided you will be prompted to enter a value ",
             action="store",
             default=""),
    argument("-nk", "--newkeystore", help="Set this to true to create a new store without any prompts using location"
                                          " defined in argument configdir", action="store_true"),
    argument("-p", "--postgrespassword",
             help="Network Gateway uses Postgres as datastore. This is password for the user `postgres`.",
             action="store",
             default=""),
    argument("-t", "--trustednode",
             help="Trusted node on radix network."
                  "Example format: 'radix://node_tdx_e_1q0gm3fwqh8ggl09g7l8ru96krzlxdyrc694mqw8cf227v62vjyrmccv8md5@13.126.65.118'."
                  "This is required only if you are creating config to run a CORE node and "
                  "if not provided you will be prompted to enter a value",
             default="",
             action="store"),
    argument("-v", "--validator", help="Address of the validator ", action="store"),
    argument("-xc", "--disablenginxforcore", help="Core Node API's are protected by Basic auth setting."
                                                  "Set this to disable to nginx for core",
             action="store", default="", choices=["true", "false"]),
    argument("-xg", "--disablenginxforgateway", help="GateWay API's end points are protected by Basic auth settings. "
                                                     "Set this to disable to nginx for gateway",
             action="store", default="", choices=["true", "false"])
])
def config(args):
    """
    This commands allows node-runners and gateway admins to create a config file, which can persist their custom settings.
    Thus it allows is to decouple the updates from docker_config.
    Config is created only once as such and if there is a version change in the config file,
    then it updated by doing a migration to newer version
    """

    ################### PARSE ARGUMENTS
    argument_object = DockerConfigArguments(args)
    if "DETAILED" in argument_object.setupmode.mode and len(argument_object.setupmode.mode) > 1:
        if "CORE" in argument_object.setupmode.mode or "GATEWAY" in argument_object.setupmode.mode:
            print(f"{bcolors.FAIL}You cannot have DETAILED option with other options together."
                  f"\nDETAILED option goes through asking each and every question that to customize setup. "
                  f"Hence cannot be clubbed together with options"
                  f"{bcolors.ENDC}")
            sys.exit(1)
        else:
            if len(argument_object.setupmode.mode) == 2 and "MIGRATION" in argument_object.setupmode.mode:
                logger.info(f"Running modes: {argument_object.setupmode.mode}")
            else:
                logger.error(f"Mode: {argument_object.setupmode.mode}. Not supported. Exiting")
                sys.exit(1)

    ################### QUESTIONARY
    docker_config = DockerSetup.questionary(argument_object)

    ################### Saving Answers
    Path(f"{Helpers.get_default_node_config_dir()}").mkdir(parents=True, exist_ok=True)
    DockerSetup.print_config(docker_config)
    DockerSetup.compare_config_file_with_config_object(argument_object.config_file, docker_config)
    DockerSetup.save_config(docker_config, argument_object.config_file, argument_object.autoapprove)


@dockercommand([
    argument("-a", "--autoapprove", help="Pass this option to run without any prompts. "
                                         "Use this for automation purpose only", action="store_true"),
    argument("-aue", "--advanceduserenvs",
             help="Path to advanced config file. This file can directly configure the core node. "
                  "It is templated into default.config and acts as custom configuration that is not overwritten on install. "
                  f"The default value is `{Helpers.get_default_node_config_dir()}/advanced-user.default.config` if not provided",
             default=f"{Helpers.get_default_node_config_dir()}/advanced-user.default.config",
             action="store"),
    argument("-f", "--configfile",
             help="Path to config file. This file is generated by running 'babylonnode docker config'"
                  f"The default value is `{Helpers.get_default_node_config_dir()}/config.yaml` if not provided",
             default=f"{Helpers.get_default_node_config_dir()}/config.yaml",
             action="store"),
    argument("-u", "--update", help="Pass this option to update the deployed softwares to latest version."
                                    " CLI prompts to confirm the versions if '-a' is not passed", action="store_true")
])
def install(args):
    """
    This commands setups up the software and deploys it based on what is stored in the config.yaml file.
    To update software versions, most of the time it is required to update the versions in config file and run this command
    """
    ########## Parse Arguments
    argument_object = DockerInstallArguments(args)

    ########## Update existing Config
    docker_config: DockerConfig = DockerSetup.load_settings(argument_object.config_file)
    docker_config_updated_versions = DockerSetup.update_versions(docker_config,
                                                                 argument_object.autoapprove) if argument_object.update else docker_config

    docker_config_updated_versions = DockerSetup.check_set_passwords(docker_config_updated_versions)
    DockerSetup.confirm_config_changes(argument_object, docker_config, docker_config_updated_versions)

    ########## Install dependent services
    DockerSetup.conditionally_start_local_postgres(docker_config_updated_versions)

    if docker_config.core_node is not None:
        DockerSetup.chown_files(docker_config)

    ########## Render Docker Compose
    if args.advanceduserenvs != "":
        if os.path.exists(args.advanceduserenvs):
            docker_config_updated_versions.advanced_user_envs = args.advanceduserenvs
    compose_file = DockerSetup.confirm_docker_compose_file_changes(docker_config_updated_versions,
                                                                   argument_object.autoapprove)

    DockerCompose.confirm_run_docker_compose(argument_object, compose_file)


@dockercommand([
    argument("-f", "--configfile",
             default=f"{Helpers.get_default_node_config_dir()}/config.yaml",
             help="Path to config file. This file is generated by running 'babylonnode docker config'"
                  f"The default value is `{Helpers.get_default_node_config_dir()}/config.yaml` if not provided",
             action="store"),
])
def start(args):
    """
    This commands starts the docker containers based on what is stored in the config.yaml file.
    If you have modified the config file, it is advised to use setup command.
    """
    ########## Load settings from file
    docker_config = DockerSetup.load_settings(args.configfile)
    docker_config = DockerSetup.check_set_passwords(docker_config)
    ########## Install dependent services
    DockerSetup.conditionally_start_local_postgres(docker_config)
    compose = DockerSetup.get_existing_compose_file(docker_config.common_config.docker_compose)
    if compose is None:
        print("No docker-compose file found.")
        print("Execute `babylonnode docker config/install` and try again")
        sys.exit(404)
    DockerCompose.run_docker_compose_up(docker_config.common_config.docker_compose)


@dockercommand([
    argument("-f", "--composefile",
             help="Path to docker-compose file. This file is generated by running 'babylonnode docker install'"
                  f"The default value is `{Helpers.get_home_dir()}/docker-compose.yml` if not provided",
             default=f"{Helpers.get_home_dir()}/docker-compose.yml",
             action="store"),
    argument("-v", "--removevolumes", help="Remove the volumes ", default=False, action="store_true"),
])
def stop(args):
    """
    This commands stops the docker containers
    """
    if args.removevolumes:
        print(
            """ 
            Removing volumes including Nginx volume. Nginx password needs to be recreated again when you bring node up
            """)
    compose = DockerSetup.get_existing_compose_file(args.composefile)
    if compose is None:
        print("No docker-compose file found.")
        print("Execute `babylonnode docker config/install` and try again")
        sys.exit(404)
    DockerCompose.run_docker_compose_down(args.composefile, args.removevolumes)


@dockercommand([
    argument("-f", "--configfile",
             default=f"{Helpers.get_default_node_config_dir()}/config.yaml",
             help="Path to config file. This file is generated by running 'babylonnode docker config'"
                  f"The default value is `{Helpers.get_default_node_config_dir()}/config.yaml` if not provided",
             action="store"),
    argument("-a", "--autoapprove", help="Set this to true to run without any prompts"
                                         "Use this for automation purpose only", action="store_true", default=False),
])
def generate(args):
    """
    This commands generates a docker-compose file from existing config files.
    """
    ########## Load settings from file
    docker_config = DockerSetup.load_settings(args.configfile)
    docker_config = DockerSetup.check_set_passwords(docker_config)
    DockerSetup.confirm_docker_compose_file_changes(docker_config, args.autoapprove)


@dockercommand([])
def dependencies(args):
    """
    This commands installs all necessary software on the Virtual Machine(VM).
    Run this command on fresh VM or on a existing VM  as the command is tested to be idempotent
    """
    logger.info("Installing docker dependencies")
    BaseSetup.dependencies()
