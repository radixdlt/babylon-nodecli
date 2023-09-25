import sys
from argparse import ArgumentParser
from os.path import exists
from pathlib import Path

from commands.subcommand import get_decorator, argument
from config.SystemDConfig import SystemDConfig
from setup.BaseSetup import BaseSetup
from setup.DockerCompose import DockerCompose
from setup.GatewaySetup import GatewaySetup
from setup.SystemDCommandArguments import SystemDConfigArguments
from setup.SystemDSetup import SystemDSetup
from utils.utils import Helpers, bcolors

systemdcli = ArgumentParser(
    description='Subcommand to help setup CORE using systemD service',
    usage="babylonnode systemd ")
systemd_parser = systemdcli.add_subparsers(dest="systemdcommand")


def systemdcommand(systemdcommand_args=None, parent=systemd_parser):
    if systemdcommand_args is None:
        systemdcommand_args = []
    return get_decorator(systemdcommand_args, parent)


@systemdcommand([
    argument("-a", "--autoapprove", help="Set this to true to run without any prompts and in mode CORE."
                                         "Prompts still appear if you run in DETAILED mode "
                                         "Use this for automation purpose only", action="store_true", default=False),
    argument("-d", "--configdir",
             help=f"Path to node-config directory where config file will stored. Default value is {Helpers.get_default_node_config_dir()}",
             action="store",
             default=f"{Helpers.get_default_node_config_dir()}"),
    argument("-dd", "--data_directory", help="Folder for data generated by the node", action="store"),
    argument("-i", "--hostip", help="Static Public IP of the node", action="store"),
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
              \n\nDETAILED: Default value if not provided. This mode takes your through series of questions.
              \n\nGATEWAY: This mode adds questions regarding the Network Gateway API and enables it for installation
              \n\nMIGRATION: This mode adds questions regarding the migration from an Olympia End-State node to a Babylon node
              """,
             choices=["CORE", "DETAILED", "MIGRATION", "GATEWAY"], action="store"),
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
    argument("-r", "--release",
             help="Version of node software to install",
             action="store"),
    argument("-t", "--trustednode", help="Trusted node on radix network", action="store"),
    argument("-v", "--validator", help="Address of the validator ", action="store"),
    argument("-x", "--nginxrelease", help="Version of radixdlt nginx release ", action="store"),
    argument("-xc", "--disablenginxforcore", help="Core Node API's are protected by Basic auth setting."
                                                  "Set this to disable to nginx for core",
             action="store", default="", choices=["true", "false"]),
])
def config(args):
    """
    This commands allows node-runners and gateway admins to create a config file, which can persist their custom
    settings. Thus, it allows is to decouple the updates from systemd_config. Config is created only once as such and
    if there is a version change in the config file, then it updated by doing a migration to newer version
    """
    # Systemd configure is setup using radixdlt user. And this user has been added to docker group yet.
    # EDIT: This command is already executed by the dependency command. Running this here prevents us from executing
    #       tests on the config command from macos.
    # BaseSetup.add_user_docker_group()

    ################### PARSE ARGUMENTS
    argument_object = SystemDConfigArguments(args)

    ################### QUESTIONARY
    print_questionary_header(argument_object.config_file)

    systemd_config = SystemDConfig({})

    systemd_config.common_config = SystemDSetup.ask_common_config(argument_object)
    systemd_config.core_node = SystemDSetup.ask_core_node(argument_object)
    if "GATEWAY" in argument_object.setupmode.mode:
        systemd_config.gateway = GatewaySetup.ask_gateway_standalone_docker("")
    systemd_config.migration = SystemDSetup.ask_migration(argument_object)

    ################### File comparisson and generation
    Path(f"{args.configdir}").mkdir(parents=True, exist_ok=True)
    Path(f"{args.data_directory}").mkdir(parents=True, exist_ok=True)
    SystemDSetup.dump_config_as_yaml(systemd_config)

    # Compare old and new if and only if there's an old
    if exists(argument_object.config_file):
        SystemDSetup.compare_old_and_new_config(argument_object.config_file, systemd_config)
    SystemDSetup.save_config(systemd_config, argument_object.config_file, autoapprove=args.autoapprove)


@systemdcommand([
    argument("-a", "--auto", help="Automatically approve all Yes/No prompts", action="store_true"),
    argument("-u", "--update", help="Update the node to new version of node", action="store_true"),
    argument("-f", "--configfile",
             help="Path to config file. This file is generated by running 'babylonnode systemd config'"
                  f"The default value is `{Helpers.get_default_node_config_dir()}/config.yaml` if not provided",
             default=f"{Helpers.get_default_node_config_dir()}/config.yaml",
             action="store"),
    argument("-m", "--manual", help="Only generate systemd file but not put it into systemd folder."
                                    "This is mainly used for automation in unprivileged environments.",
             action="store_true"),
])
def install(args):
    """This sets up the systemd service for the core node."""
    settings: SystemDConfig = SystemDSetup.load_settings(args.configfile)
    if args.update:
        settings = BaseSetup.update_versions(settings, args.auto)
    SystemDSetup.install_systemd_service(settings, args)


@systemdcommand([
    argument("-s", "--services", default="all",
             help="Name of the service either to be stopped. Valid values nginx or radixdlt-node",
             choices=["all", "nginx", "radixdlt-node"], action="store")
])
def stop(args):
    """This stops the CORE node systemd service."""
    if args.services == "all":
        SystemDSetup.stop_nginx_service()
        SystemDSetup.stop_node_service()
        DockerCompose.stop_gateway_containers()
    elif args.services == "nginx":
        SystemDSetup.stop_nginx_service()
    elif args.services == "radixdlt-node":
        SystemDSetup.stop_node_service()
    else:
        print(f"Invalid service name {args.services}")
        sys.exit(1)


@systemdcommand([
    argument("-s", "--services", default="all",
             help="Name of the service either to be started. Valid values nginx or radixdlt-node",
             choices=["all", "nginx", "radixdlt-node"], action="store")
])
def start(args):
    """This starts the CORE node systemd service."""
    if args.services == "all":
        SystemDSetup.restart_node_service()
        SystemDSetup.restart_nginx_service()
        DockerCompose.restart_gateway_containers()
    elif args.services == "nginx":
        SystemDSetup.restart_nginx_service()
    elif args.services == "radixdlt-node":
        SystemDSetup.restart_node_service()
    else:
        print(f"Invalid service name {args.services}")
        sys.exit(1)


@systemdcommand([
    argument("-s", "--services", default="all",
             help="Name of the service either to be started. Valid values nginx or radixdlt-node",
             choices=["all", "nginx", "radixdlt-node"], action="store")
])
def restart(args):
    """This restarts the CORE node systemd service."""
    if args.services == "all":
        SystemDSetup.restart_node_service()
        SystemDSetup.restart_nginx_service()
        DockerCompose.restart_gateway_containers()
    elif args.services == "nginx":
        SystemDSetup.restart_nginx_service()
    elif args.services == "radixdlt-node":
        SystemDSetup.restart_node_service()
    else:
        print(f"Invalid service name {args.services}")
        sys.exit(1)


@systemdcommand([
    argument("-s", "--skip", default=False,
             help="Skip installation of base dependencies",
             action="store_true")
])
def dependencies(args):
    """
    This commands installs all necessary software on the Virtual Machine(VM).
    Run this command on fresh VM or on an existing VM  as the command is tested to be idempotent
    """

    if not args.skip:
        BaseSetup.dependencies()
    SystemDSetup.install_java()
    SystemDSetup.setup_user()
    BaseSetup.add_radixdlt_user_docker_group()
    SystemDSetup.make_etc_directory()
    SystemDSetup.make_data_directory()
    SystemDSetup.create_service_user_password()
    SystemDSetup.create_initial_service_file()
    SystemDSetup.sudoers_instructions()


def print_questionary_header(config_file):
    Helpers.section_headline("CONFIG FILE")
    print(
        "\nCreating config file using the answers from the questions that would be asked in next steps."
        f"\nLocation of the config file: {bcolors.OKBLUE}{config_file}{bcolors.ENDC}")
