import ipaddress
import sys
from argparse import ArgumentParser
from pathlib import Path

import yaml
from deepdiff import DeepDiff

from commands.subcommand import get_decorator, argument
from config.BaseConfig import SetupMode
from config.SystemDConfig import SystemDSettings, CoreSystemdSettings, CommonSystemdSettings
from github.github import latest_release
from setup.Base import Base
from setup.SystemD import SystemD
from utils.utils import Helpers, bcolors

systemdcli = ArgumentParser(
    description='Subcommand to help setup CORE using systemD service',
    usage="radixnode systemd ")
systemd_parser = systemdcli.add_subparsers(dest="systemdcommand")


def systemdcommand(systemdcommand_args=None, parent=systemd_parser):
    if systemdcommand_args is None:
        systemdcommand_args = []
    return get_decorator(systemdcommand_args, parent)


@systemdcommand([
    argument("-a", "--autoapprove", help="Set this to true to run without any prompts and in mode CORE."
                                         "Prompts still appear if you run in DETAILED mode "
                                         "Use this for automation purpose only", action="store_true"),
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
              """,
             choices=["CORE", "DETAILED", "MIGRATION"], action="store"),
    argument("-miu", "--migration_url", help="The url of the olympia node to migrate the ledger from", action="store"),
    argument("-miau", "--migration_auth_user", help="The user to authenticate to the olympia node for migration",
             action="store"),
    argument("-miap", "--migration_auth_password",
             help="The password to authenticate to the olympia node for migration", action="store"),
    argument("-miba", "--migration_bech_url", help="The bech url of the olympia node to migrate the ledger from",
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
    settings. Thus, it allows is to decouple the updates from configuration. Config is created only once as such and
    if there is a version change in the config file, then it updated by doing a migration to newer version
    """

    # make default object
    # add values from arguments and do validations
    # ask for values and do validation differently -> do validations the same way.

    if args.hostip:
        try:
            ipaddress.ip_address(args.hostip)
        except ValueError:
            print(f"'{args.hostip}' is not a valid ip address.")
            sys.exit(1)

    setupmode = SetupMode.instance()
    setupmode.mode = args.setupmode

    trustednode = args.trustednode if args.trustednode != "" else None
    keystore_password = args.keystorepassword if args.keystorepassword != "" else None
    nginx_on_core = args.disablenginxforcore if args.disablenginxforcore != "" else None
    data_directory = args.data_directory
    new_keystore = args.newkeystore

    olympia_node_url = args.migration_url
    olympia_node_bech32_address = args.migration_auth_user
    olympia_node_auth_user = args.migration_auth_user
    olympia_node_auth_password = args.migration_auth_password

    Helpers.section_headline("CONFIG FILE")
    config_file = f"{args.configdir}/config.yaml"
    Path(f"{args.configdir}").mkdir(parents=True, exist_ok=True)
    print(
        "\nCreating config file using the answers from the questions that would be asked in next steps."
        f"\nLocation of the config file: {bcolors.OKBLUE}{config_file}{bcolors.ENDC}")
    config_to_dump = {"version": "0.1"}
    if not args.release:
        release = latest_release()
    else:
        release = args.release

    configuration = SystemDSettings({})
    configuration.common_config = CommonSystemdSettings({})
    configuration.common_config.ask_network_id(args.networkid)
    configuration.common_config.ask_host_ip(args.hostip)
    configuration.core_node.ask_validator_address(args.validator)

    configuration.core_node = CoreSystemdSettings({}).create_config(release, data_directory,
                                                                    trustednode,
                                                                    keystore_password, new_keystore)
    configuration.common_config.ask_enable_nginx_for_core(nginx_on_core)

    if "MIGRATION" in setupmode.mode:
        configuration.migration.ask_migration_config(olympia_node_url, olympia_node_auth_user,
                                                     olympia_node_auth_password,
                                                     olympia_node_bech32_address)

    config_to_dump["core_node"] = dict(configuration.core_node)

    if configuration.common_config.check_nginx_required():
        configuration.common_config.ask_nginx_release()
    else:
        configuration.common_config.nginx_settings = None

    config_to_dump["common_config"] = dict(configuration.common_config)

    yaml.add_representer(type(None), Helpers.represent_none)
    Helpers.section_headline("CONFIG is Generated as below")
    print(f"\n{yaml.dump(config_to_dump)}")

    old_config = SystemD.load_all_config(config_file)
    if len(old_config) != 0:
        print(f"""
                {Helpers.section_headline("Differences")}
                Difference between existing config file and new config that you are creating
                {dict(DeepDiff(old_config, config_to_dump))}
                  """)

    SystemD.save_settings(configuration, config_file, autoapprove=args.autoapprove)


@systemdcommand([
    argument("-a", "--auto", help="Automatically approve all Yes/No prompts", action="store_true"),
    argument("-u", "--update", help="Update the node to new version of node", action="store_true"),
    argument("-f", "--configfile",
             help="Path to config file. This file is generated by running 'radixnode systemd config'"
                  f"The default value is `{Helpers.get_default_node_config_dir()}/config.yaml` if not provided",
             default=f"{Helpers.get_default_node_config_dir()}/config.yaml",
             action="store"),
    argument("-m", "--manual", help="Only generate systemd file but not put it into systemd folder."
                                    "This is mainly used for automation in unprivileged environments.",
             action="store_true"),
])
def install(args):
    """This sets up the systemd service for the core node."""
    auto_approve = args.auto
    settings = SystemD.load_settings(args.configfile)

    print("--------------------------------")
    print("\nUsing following configuration:")
    print("\n--------------------------------")
    print(settings.to_yaml())

    if auto_approve is None:
        SystemD.confirm_config(settings.core_node.nodetype,
                               settings.core_node.core_release,
                               settings.core_node.core_binary_url,
                               settings.common_config.nginx_settings.config_url)

    SystemD.checkUser()

    SystemD.download_binaries(binary_location_url=settings.core_node.core_binary_url,
                              library_location_url=settings.core_node.core_library_url,
                              node_dir=settings.core_node.node_dir,
                              node_version=settings.core_node.core_release,
                              auto_approve=auto_approve)

    backup_time = Helpers.get_current_date_time()

    settings.create_default_config()
    SystemD.backup_file(settings.core_node.node_dir, f"default.config", backup_time, auto_approve)

    # Below steps only required if user want's setup nginx in same node
    SystemD.backup_file("/lib/systemd/system", "nginx.service", backup_time, auto_approve)
    SystemD.create_ssl_certs(settings.common_config.nginx_settings.secrets_dir, auto_approve)
    nginx_configured = SystemD.setup_nginx_config(
        nginx_config_location_url=settings.common_config.nginx_settings.config_url,
        node_type=settings.core_node.nodetype,
        nginx_etc_dir=settings.common_config.nginx_settings.dir, backup_time=backup_time,
        auto_approve=auto_approve)

    # Core node environment files
    SystemD.backup_file(settings.core_node.node_secrets_dir, "environment", backup_time, auto_approve)
    settings.create_environment_file()
    # Core node systemd service file
    SystemD.backup_file("/etc/systemd/system", "radixdlt-node.service", backup_time, auto_approve)
    service_file_path = "/etc/systemd/system/radixdlt-node.service"
    if args.manual:
        service_file_path = f"{settings.core_node.node_dir}/radixdlt-node.service"
    settings.create_service_file(service_file_path)

    if not args.manual:
        if not args.update:
            SystemD.start_node_service()
        else:
            SystemD.restart_node_service()

        if nginx_configured and not args.update:
            SystemD.start_nginx_service()
        elif nginx_configured and args.update:
            SystemD.start_nginx_service()
        else:
            print("Nginx not configured or not updated")


@systemdcommand([
    argument("-s", "--services", default="all",
             help="Name of the service either to be stopped. Valid values nginx or radixdlt-node",
             choices=["all", "nginx", "radixdlt-node"], action="store")
])
def stop(args):
    """This stops the CORE node systemd service."""
    if args.services == "all":
        SystemD.stop_nginx_service()
        SystemD.stop_node_service()
    elif args.services == "nginx":
        SystemD.stop_nginx_service()
    elif args.services == "radixdlt-node":
        SystemD.stop_node_service()
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
        SystemD.restart_node_service()
        SystemD.restart_nginx_service()
    elif args.services == "nginx":
        SystemD.restart_nginx_service()
    elif args.services == "radixdlt-node":
        SystemD.restart_node_service()
    else:
        print(f"Invalid service name {args.services}")
        sys.exit(1)


@systemdcommand([])
def dependencies(args):
    """
    This commands installs all necessary software on the Virtual Machine(VM).
    Run this command on fresh VM or on an existing VM  as the command is tested to be idempotent
    """

    Base.dependencies()
    SystemD.install_java()
    SystemD.setup_user()
    SystemD.make_etc_directory()
    SystemD.make_data_directory()
    SystemD.create_service_user_password()
    SystemD.create_initial_service_file()
    SystemD.sudoers_instructions()
