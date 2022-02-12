#!/usr/bin/env python
import os
import os.path
import sys
from argparse import ArgumentParser

import system_client as system_api
import urllib3
from core_client.model.construction_build_response import ConstructionBuildResponse
from core_client.model.construction_submit_response import ConstructionSubmitResponse
from core_client.model.entity_identifier import EntityIdentifier
from core_client.model.entity_response import EntityResponse
from core_client.model.key_list_response import KeyListResponse
from core_client.model.key_sign_response import KeySignResponse
from core_client.model.sub_entity import SubEntity
from core_client.model.sub_entity_metadata import SubEntityMetadata

from api.Api import API
from api.CoreApiHelper import CoreApiHelper
from api.DefaultApiHelper import DefaultApiHelper
from api.ValidatorConfig import ValidatorConfig
from commands.authcommand import authcli
from commands.coreapi import handle_core
from commands.monitoring import monitoringcli
from env_vars import COMPOSE_FILE_OVERIDE, NODE_BINARY_OVERIDE, NGINX_BINARY_OVERIDE, DISABLE_VERSION_CHECK
from github.github import latest_release
from key_interaction.KeyInteraction import KeyInteraction
from monitoring import Monitoring
from setup import Base, Docker, SystemD
from utils.utils import Helpers, cli_version
from utils.utils import run_shell_command
from commands.key import keycli

urllib3.disable_warnings()


def get_decorator(args, parent):
    def decorator(func):
        parser = parent.add_parser(func.__name__.replace("_", "-"), description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator


def argument(*name_or_flags, **kwargs):
    return list(name_or_flags), kwargs


cli = ArgumentParser()
cli.add_argument('subcommand', help='Subcommand to run',
                 choices=["docker", "systemd", "api", "monitoring", "version", "optimise-node", "auth", "key"])

apicli = ArgumentParser(
    description='API commands')
api_parser = apicli.add_argument(dest="apicommand",
                                 choices=["system", "core"])

cwd = os.getcwd()

dockercli = ArgumentParser(
    description='Docker commands')
docker_parser = dockercli.add_subparsers(dest="dockercommand")


def dockercommand(dockercommand_args=[], parent=docker_parser):
    return get_decorator(dockercommand_args, parent)


systemdcli = ArgumentParser(
    description='Systemd commands')
systemd_parser = systemdcli.add_subparsers(dest="systemdcommand")


def systemdcommand(systemdcommand_args=[], parent=systemd_parser):
    return get_decorator(systemdcommand_args, parent)




systemapicli = ArgumentParser(
    description='systemapi commands')
systemapi_parser = systemapicli.add_subparsers(dest="systemapicommand")


def systemapicommand(args=[], parent=systemapi_parser):
    return get_decorator(args, parent)




def print_cli_version():
    print(f"Cli - Version : {cli_version()}")


@dockercommand([

    argument("-n", "--nodetype", required=True, default="fullnode", help="Type of node fullnode or archivenode",
             action="store", choices=["fullnode", "archivenode"]),
    argument("-t", "--trustednode", required=True,
             help="Trusted node on radix network. Example format: radix//brn1q0mgwag0g9f0sv9fz396mw9rgdall@10.1.2.3",
             action="store"),
    argument("-u", "--update", help="Update the node to new version of composefile", action="store_false"),
])
def setup(args):
    release = latest_release()

    if args.nodetype == "archivenode":
        Helpers.archivenode_deprecate_message()

    composefileurl = os.getenv(COMPOSE_FILE_OVERIDE,
                               f"https://raw.githubusercontent.com/radixdlt/node-runner/{cli_version()}/node-runner-cli/release_ymls/radix-{args.nodetype}-compose.yml")
    print(f"Going to setup node type {args.nodetype} from location {composefileurl}.\n")
    # TODO autoapprove
    continue_setup = input(
        "Do you want to continue [Y/n]?:")

    if not Helpers.check_Yes(continue_setup):
        print(" Quitting ....")
        sys.exit()

    keystore_password, file_location = Base.generatekey(keyfile_path=Helpers.get_keyfile_path(), keygen_tag=release)
    Docker.setup_compose_file(composefileurl, file_location)

    trustednode_ip = Helpers.parse_trustednode(args.trustednode)

    compose_file_name = composefileurl.rsplit('/', 1)[-1]
    action = "update" if args.update else "start"
    print(f"About to {action} the node using docker-compose file {compose_file_name}, which is as below")
    run_shell_command(f"cat {compose_file_name}", shell=True)
    # TODO AutoApprove
    should_start = input(f"\nOkay to start the node [Y/n]?:")
    if Helpers.check_Yes(should_start):
        if action == "update":
            print(f"For update, bringing down the node using compose file {compose_file_name}")
            Docker.run_docker_compose_down(compose_file_name)
        Docker.run_docker_compose_up(keystore_password, compose_file_name, args.trustednode)
    else:
        print(f"""
            ---------------------------------------------------------------
            Bring up node by updating the file {compose_file_name}
            You can do it through cli using below command
                radixnode docker stop  -f {compose_file_name}
                radixnode docker start -f {compose_file_name} -t {args.trustednode}
            ----------------------------------------------------------------
            """)


@systemdcommand([
    argument("-r", "--release",
             help="Version of node software to install",
             action="store"),
    argument("-x", "--nginxrelease", help="Version of radixdlt nginx release ", action="store"),
    argument("-t", "--trustednode", required=True, help="Trusted node on radix network", action="store"),
    argument("-n", "--nodetype", required=True, default="fullnode", help="Type of node fullnode or archivenode",
             action="store", choices=["fullnode", "archivenode"]),
    argument("-i", "--hostip", required=True, help="Static Public IP of the node", action="store"),
    argument("-u", "--update", help="Update the node to new version of node", action="store_false"),

])
def setup(args):
    if not args.release:
        release = latest_release()
    else:
        release = args.release

    if not args.nginxrelease:
        nginx_release = latest_release("radixdlt/radixdlt-nginx")
    else:
        nginx_release = args.nginxrelease

    if args.nodetype == "archivenode":
        Helpers.archivenode_deprecate_message()

    node_type_name = 'fullnode'
    node_dir = '/etc/radixdlt/node'
    nginx_dir = '/etc/nginx'
    nginx_secrets_dir = f"{nginx_dir}/secrets"
    node_secrets_dir = f"{node_dir}/secrets"
    nodebinaryUrl = os.getenv(NODE_BINARY_OVERIDE,
                              f"https://github.com/radixdlt/radixdlt/releases/download/{release}/radixdlt-dist-{release}.zip")

    # TODO add method to fetch latest nginx release
    nginxconfigUrl = os.getenv(NGINX_BINARY_OVERIDE,
                               f"https://github.com/radixdlt/radixdlt-nginx/releases/download/{nginx_release}/radixdlt-nginx-{node_type_name}-conf.zip")
    # TODO AutoApprove
    continue_setup = input(
        f"Going to setup node type {args.nodetype} for version {release} from location {nodebinaryUrl} and {nginxconfigUrl}. \n Do you want to continue Y/n:")

    if not Helpers.check_Yes(continue_setup):
        print(" Quitting ....")
        sys.exit()

    backup_time = Helpers.get_current_date_time()
    SystemD.checkUser()
    keystore_password, keyfile_location = SystemD.generatekey(node_secrets_dir, keygen_tag=release)
    trustednode_ip = Helpers.parse_trustednode(args.trustednode)

    SystemD.backup_file(node_secrets_dir, f"environment", backup_time)
    SystemD.set_environment_variables(keystore_password, node_secrets_dir)

    SystemD.backup_file(node_dir, f"default.config", backup_time)

    SystemD.setup_default_config(trustednode=args.trustednode, hostip=args.hostip, node_dir=node_dir,
                                 node_type=args.nodetype)

    node_version = nodebinaryUrl.rsplit('/', 2)[-2]
    SystemD.backup_file("/etc/systemd/system", "radixdlt-node.service", backup_time)
    SystemD.setup_service_file(node_version, node_dir=node_dir, node_secrets_path=node_secrets_dir)

    SystemD.download_binaries(nodebinaryUrl, node_dir=node_dir, node_version=node_version)

    SystemD.backup_file("/lib/systemd/system", f"nginx.service", backup_time)

    nginx_configured = SystemD.setup_nginx_config(nginx_config_location_Url=nginxconfigUrl,
                                                  node_type=args.nodetype,
                                                  nginx_etc_dir=nginx_dir, backup_time=backup_time)
    SystemD.create_ssl_certs(nginx_secrets_dir)
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


@dockercommand([
    argument("-f", "--composefile", required=True, help="The name of compose file ", action="store"),
    argument("-t", "--trustednode", required=True, help="Trusted node on radix network", action="store")
])
def start(args):
    release = latest_release()
    keystore_password, keyfile_location = Base.generatekey(keyfile_path=Helpers.get_keyfile_path(), keygen_tag=release)
    Docker.run_docker_compose_up(keystore_password, args.composefile, args.trustednode)


@dockercommand([
    argument("-f", "--composefile", required=True, help="The name of compose file ", action="store"),
    argument("-v", "--removevolumes", help="Remove the volumes ", action="store_true"),
])
def stop(args):
    if args.removevolumes:
        print(
            """ 
            Removing volumes including Nginx volume. Nginx password needs to be recreated again when you bring node up
            """)
    Docker.run_docker_compose_down(args.composefile, args.removevolumes)


@dockercommand([])
def configure(args):
    Base.install_dependecies()
    Base.add_user_docker_group()


@systemdcommand([])
def configure(args):
    Base.install_dependecies()
    SystemD.install_java()
    SystemD.setup_user()
    SystemD.make_etc_directory()
    SystemD.make_data_directory()
    SystemD.create_service_user_password()
    SystemD.create_initial_service_file()
    SystemD.sudoers_instructions()


@systemapicommand()
def metrics(args):
    defaultApiHelper = DefaultApiHelper(verify_ssl=False)
    defaultApiHelper.metrics()


@systemapicommand()
def version(args):
    defaultApiHelper = DefaultApiHelper(verify_ssl=False)
    defaultApiHelper.version()


@systemapicommand()
def health(args):
    defaultApiHelper = DefaultApiHelper(verify_ssl=False)
    defaultApiHelper.health(print_response=True)


def optimise_node():
    Base.setup_node_optimisation_config(cli_version())


def check_latest_cli():
    cli_latest_version = latest_release("radixdlt/node-runner")

    if os.getenv(DISABLE_VERSION_CHECK, "False").lower() not in ("true", "yes"):
        if cli_version() != cli_latest_version:
            os_name = "ubuntu-20.04"
            print(
                f"Radixnode CLI latest version is {cli_latest_version} and current version of the binary is {cli_version()}.\n.")
            print(f"""
                ---------------------------------------------------------------
                Update the CLI by running these commands
                    wget -O radixnode https://github.com/radixdlt/node-runner/releases/download/{cli_latest_version}/radixnode-{os_name}
                    chmod +x radixnode
                    sudo mv radixnode /usr/local/bin
                """)
            abort = input("Do you want to ABORT the command now to update the cli Y/n?:")
            if Helpers.check_Yes(abort):
                sys.exit()


def handle_systemapi():
    systemcli_args = systemapicli.parse_args(sys.argv[3:])
    if systemcli_args.systemapicommand is None:
        systemapicli.print_help()
    else:
        systemcli_args.func(systemcli_args)


if __name__ == "__main__":

    args = cli.parse_args(sys.argv[1:2])

    if args.subcommand is None:
        cli.print_help()
    else:
        if args.subcommand != "version":
            check_latest_cli()

    if args.subcommand == "docker":
        dockercli_args = dockercli.parse_args(sys.argv[2:])
        if dockercli_args.dockercommand is None:
            dockercli.print_help()
        else:
            dockercli_args.func(dockercli_args)

    elif args.subcommand == "systemd":
        systemdcli_args = systemdcli.parse_args(sys.argv[2:])
        if systemdcli_args.systemdcommand is None:
            systemdcli.print_help()
        else:
            systemdcli_args.func(systemdcli_args)

    elif args.subcommand == "api":
        apicli_args = apicli.parse_args(sys.argv[2:3])
        if apicli_args.apicommand is None:
            apicli.print_help()
        else:
            if apicli_args.apicommand == "metrics":
                defaultApi = DefaultApiHelper(verify_ssl=False)
                defaultApi.prometheus_metrics()
            elif apicli_args.apicommand == "system":
                handle_systemapi()
            elif apicli_args.apicommand == "core":
                handle_core()
            else:
                print(f"Invalid api command {apicli_args.apicommand}")

    elif args.subcommand == "monitoring":
        monitoringcli_args = monitoringcli.parse_args(sys.argv[2:])
        if monitoringcli_args.monitoringcommand is None:
            monitoringcli.print_help()
        else:
            monitoringcli_args.func(monitoringcli_args)
    elif args.subcommand == "auth":
        authcli_args = authcli.parse_args(sys.argv[2:])
        if authcli_args.authcommand is None:
            authcli.print_help()
        else:
            authcli_args.func(authcli_args)
    elif args.subcommand == "key":
        keycli_args = keycli.parse_args(sys.argv[2:])
        if keycli_args.keycommand is None:
            keycli.print_help()
        else:
            keycli_args.func(keycli_args)
    elif args.subcommand == "version":
        print_cli_version()
    elif args.subcommand == "optimise-node":
        optimise_node()
    else:
        print(f"Invalid subcommand {args.subcommand}")
