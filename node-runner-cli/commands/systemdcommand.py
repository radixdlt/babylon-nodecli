import sys
from argparse import ArgumentParser

from commands.subcommand import get_decorator, argument
from setup import SystemD, Base
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
    argument("-a", "--auto", help="Automatically approve all Yes/No prompts", action="store"),
    argument("-d", "--default", help="Use default configuration where possible and dont prompt", action="store"),
    argument("-dd", "--data_directory", help="Folder for data generated by the node", action="store"),
    argument("-i", "--hostip", required=True, help="Static Public IP of the node", action="store"),
    argument("-kp", "--keystore_password", help="Set keystore password to this value", action="store"),
    argument("-n", "--network", help="The network to connect to. S for Stokenet or M for Mainnet", action="store"),
    argument("-r", "--release",
             help="Version of node software to install",
             action="store"),
    argument("-t", "--trustednode", required=True, help="Trusted node on radix network", action="store"),
    argument("-ts", "--enabletransactions", help="Enable transaction stream api", action="store_true"),
    argument("-x", "--nginxrelease", help="Version of radixdlt nginx release ", action="store"),
])
def config(args):
    """This creates all necessary config files to install the radixnode as a service."""
    auto_approve = args.auto
    keystore_password = args.keystore_password

    settings = SystemD.parse_config_from_args(args)

    backup_time = Helpers.get_current_date_time()

    if auto_approve:
        SystemD.backup_file(settings.node_secrets_dir, "node-keystore.ks", backup_time, auto_approve)

    settings.keydetails = SystemD.generatekey(keyfile_path=settings.node_secrets_dir,
                                              keygen_tag=settings.core_release,
                                              keystore_password=keystore_password,
                                              new=auto_approve)

    if settings.network_id is None:
        settings.network_id = SystemD.get_network_id()
    if settings.data_directory is None:
        settings.data_directory = Base.get_data_dir()

    SystemD.setup_default_config(trustednode=settings.trusted_node,
                                 hostip=settings.host_ip,
                                 node_dir=settings.node_dir,
                                 node_type=settings.node_type,
                                 transactions_enable=settings.enable_transaction,
                                 keyfile_location=settings.keydetails.keyfile_path,
                                 network_id=settings.network_id,
                                 data_folder=settings.data_directory)

    SystemD.backup_file(settings.node_secrets_dir, "environment", backup_time, auto_approve)

    SystemD.set_environment_variables(keystore_password=settings.keydetails.keystore_password,
                                      node_secrets_dir=settings.node_secrets_dir)

    SystemD.backup_file(settings.node_dir, f"default.config", backup_time, auto_approve)

    SystemD.backup_file("/etc/systemd/system", "radixdlt-node.service", backup_time, auto_approve)

    # save it
    SystemD.save_settings(settings)


@systemdcommand([
    argument("-a", "--auto", help="Automatically approve all Yes/No prompts", action="store"),
    argument("-u", "--update", help="Update the node to new version of node", action="store_false"),
])
def install(args):
    """This sets up the systemd service for the core node."""
    auto_approve = args.auto
    settings = SystemD.load_settings()

    if not auto_approve:
        SystemD.confirm_config(settings.node_type,
                               settings.core_release,
                               settings.node_binary_url,
                               settings.nginx.config_url)

    SystemD.checkUser()

    SystemD.download_binaries(binary_location_url=settings.node_binary_url,
                              node_dir=settings.node_dir,
                              node_version=settings.node_version,
                              auto_approve=auto_approve)

    backup_time = Helpers.get_current_date_time()
    SystemD.backup_file("/lib/systemd/system", "nginx.service", backup_time, auto_approve)

    # Missing PromptFeeder
    # Creates file. Should verify file existence and structure. ----BEGIN CERT--- etc. Maybe cert validity,expiry,etc?
    SystemD.create_ssl_certs(settings.nginx.secrets_dir, auto_approve)

    # This is actually a download command. Again check against dependencies.
    # Missing PromptFeeder
    nginx_configured = SystemD.setup_nginx_config(nginx_config_location_Url=settings.nginx.config_url,
                                                  node_type=settings.node_type,
                                                  nginx_etc_dir=settings.nginx.dir, backup_time=backup_time,
                                                  auto_approve=auto_approve)

    SystemD.setup_service_file(node_version_dir=settings.node_version,
                               node_dir=settings.node_dir,
                               node_secrets_path=settings.node_secrets_dir)

    # This can only be tested in E2E environment. This is the core functionality of this command in my eyes.
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
        sys.exit()


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
        sys.exit()


@systemdcommand([])
def dependencies(args):
    """
    This commands installs all necessary software on the Virtual Machine(VM).
    Run this command on fresh VM or on a existing VM  as the command is tested to be idempotent
    """

    # apt-get
    Base.dependencies()
    # apt-get
    SystemD.install_java()
    # Linux specific user creation
    SystemD.setup_user()
    # basic folder operations. Too simple to test
    SystemD.make_etc_directory()
    # basic folder operations. Too simple to test
    SystemD.make_data_directory()
    # User Password change.
    # Promptfeed required but not possible/easy
    SystemD.create_service_user_password()
    # basic file operations. Too simple to test
    SystemD.create_initial_service_file()
    # Info screen. Testable but nonsense
    SystemD.sudoers_instructions()
