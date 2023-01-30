import ipaddress
import sys
from argparse import ArgumentParser

from commands.subcommand import get_decorator, argument
from config.BaseConfig import SetupMode
from config.SystemDConfig import SystemDSettings
from setup.Base import Base
from setup.SystemD import SystemD
from utils.utils import Helpers

systemdcli = ArgumentParser(
    description='Subcommand to help setup CORE using systemD service',
    usage="radixnode systemd ")
systemd_parser = systemdcli.add_subparsers(dest="systemdcommand")


def systemdcommand(systemdcommand_args=None, parent=systemd_parser):
    if systemdcommand_args is None:
        systemdcommand_args = []
    return get_decorator(systemdcommand_args, parent)


@systemdcommand([
    argument("-a", "--autoapprove", help="Set this to true to run without any prompts and in mode CORE or GATEWAY."
                                         "Prompts still appear if you run in DETAILED mode "
                                         "Use this for automation purpose only", action="store_true"),
    argument("-d", "--configdir",
             help=f"Path to node-config directory where config file will stored. Default value is {Helpers.get_default_node_config_dir()}",
             action="store",
             default=f"/etc/radixdlt/node"),
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
              \n\nGATEWAY: Use this value to setup GATEWAY using defaults.
              \n\nDETAILED: Default value if not provided. This mode takes your through series of questions.
              """,
             choices=["CORE", "GATEWAY", "DETAILED"], action="store"),
    argument("-n", "--networkid",
             help="Network id of network you want to connect.For stokenet it is 2 and for mainnet it is 1."
                  "If not provided you will be prompted to enter a value ",
             action="store",
             default=""),
    argument("-r", "--release",
             help="Version of node software to install",
             action="store"),
    argument("-t", "--trustednode", help="Trusted node on radix network", action="store"),
    argument("-ts", "--enabletransactions", help="Enable transaction stream api", action="store_true"),
    argument("-x", "--nginxrelease", help="Version of radixdlt nginx release ", action="store"),
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

    auto_approve = args.autoapprove
    keystore_password = args.keystorepassword
    backup_time = Helpers.get_current_date_time()

    settings: SystemDSettings = SystemD.parse_config_from_args(args)

    settings.common_settings.ask_host_ip(args.hostip)
    settings.core_node_settings.ask_enable_transaction(args.enabletransactions)
    settings.core_node_settings.ask_trusted_node(args.trustednode)
    settings.common_settings.ask_network_id(args.networkid)
    settings.core_node_settings.ask_data_directory(args.data_directory)

    if auto_approve:
        SystemD.backup_file(settings.common_settings.node_secrets_dir, "node-keystore.ks", backup_time, auto_approve)

    settings.core_node_settings.keydetails = SystemD.generatekey(
        keyfile_path=settings.core_node_settings.keydetails.keyfile_path,
        keygen_tag=settings.core_node_settings.core_release,
        keystore_password=keystore_password,
        new=auto_approve)

    SystemD.setup_default_config(trustednode=settings.core_node_settings.trusted_node,
                                 hostip=settings.common_settings.host_ip,
                                 node_dir=settings.common_settings.node_dir,
                                 node_type=settings.core_node_settings.nodetype,
                                 transactions_enable=settings.core_node_settings.enable_transaction,
                                 keyfile_location=settings.core_node_settings.keydetails.keyfile_path,
                                 network_id=settings.common_settings.network_id,
                                 data_folder=settings.core_node_settings.data_directory)

    SystemD.backup_file(settings.common_settings.node_secrets_dir, "environment", backup_time, auto_approve)

    SystemD.set_environment_variables(keystore_password=settings.core_node_settings.keydetails.keystore_password,
                                      node_secrets_dir=settings.common_settings.node_secrets_dir)

    SystemD.backup_file(settings.common_settings.node_dir, f"default.config", backup_time, auto_approve)

    SystemD.save_settings(settings, f"{settings.common_settings.node_dir}/config.yaml")


@systemdcommand([
    argument("-a", "--auto", help="Automatically approve all Yes/No prompts", action="store_false"),
    argument("-u", "--update", help="Update the node to new version of node", action="store_false"),
    argument("-f", "--configfile",
             help="Path to config file. This file is generated by running 'radixnode docker config'"
                  f"The default value is `/etc/radixdlt/node/config.yaml` if not provided",
             default=f"/etc/radixdlt/node/config.yaml",
             action="store"),
])
def install(args):
    """This sets up the systemd service for the core node."""
    auto_approve = args.auto
    settings = SystemD.load_settings(args.configfile)

    if auto_approve is None:
        SystemD.confirm_config(settings.core_node_settings.nodetype,
                               settings.core_node_settings.core_release,
                               settings.core_node_settings.core_binary_url,
                               settings.common_settings.nginx_settings.config_url)

    SystemD.checkUser()

    SystemD.download_binaries(binary_location_url=settings.core_node_settings.core_binary_url,
                              node_dir=settings.common_settings.node_dir,
                              node_version=settings.core_node_settings.core_release,
                              auto_approve=auto_approve)

    backup_time = Helpers.get_current_date_time()
    SystemD.backup_file("/lib/systemd/system", "nginx.service", backup_time, auto_approve)

    SystemD.create_ssl_certs(settings.common_settings.nginx_settings.secrets_dir, auto_approve)

    nginx_configured = SystemD.setup_nginx_config(
        nginx_config_location_url=settings.common_settings.nginx_settings.config_url,
        node_type=settings.core_node_settings.nodetype,
        nginx_etc_dir=settings.common_settings.nginx_settings.dir, backup_time=backup_time,
        auto_approve=auto_approve)

    SystemD.backup_file("/etc/systemd/system", "radixdlt-node.service", backup_time, auto_approve)

    SystemD.setup_service_file(node_version_dir=settings.core_node_settings.core_release,
                               node_dir=settings.common_settings.node_dir,
                               node_secrets_path=settings.common_settings.node_secrets_dir)

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
