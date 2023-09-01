#!/usr/bin/env python
import os
import os.path
import sys
from argparse import ArgumentParser

import urllib3

from api.SystemApiHelper import SystemApiHelper
from commands.authcommand import authcli
from commands.dockercommand import dockercli
from commands.ledgercommand import ledgercli
from commands.key import keycli
from commands.monitoring import monitoringcli
from commands.othercommands import other_command_cli
from commands.systemapi import handle_systemapi
from commands.systemdcommand import systemdcli
from config.EnvVars import DISABLE_VERSION_CHECK
from github.github import latest_release
from log_util.logger import get_logger
from utils.utils import Helpers

urllib3.disable_warnings()

cli = ArgumentParser()
cli.add_argument('subcommand', help='Subcommand to run',
                 choices=["docker", "systemd", "api", "monitoring", "version", "optimise-node", "auth", "key", "ledger"])

apicli = ArgumentParser(
    description='API commands')
api_parser = apicli.add_argument(dest="apicommand",
                                 choices=["system", "core", "metrics"])

cwd = os.getcwd()
logger = get_logger(__name__)


def check_latest_cli():
    cli_latest_version = latest_release("radixdlt/babylon-nodecli")

    if os.getenv(DISABLE_VERSION_CHECK, "False").lower() not in ("true", "yes"):
        if Helpers.cli_version() != cli_latest_version:
            os_name = "ubuntu-22.04"
            logger.info(
                f"babylonnode CLI latest version is {cli_latest_version} and current version of the binary is {Helpers.cli_version()}.\n.")
            logger.info(f"""
                ---------------------------------------------------------------
                Update the CLI by running these commands
                    wget -O babylonnode https://github.com/radixdlt/babylon-nodecli/releases/download/{cli_latest_version}/babylonnode-{os_name}
                    chmod +x babylonnode
                    sudo mv babylonnode /usr/local/bin
                """)


def main():
    args = cli.parse_args(sys.argv[1:2])

    if args.subcommand is None:
        cli.print_help()
    else:
        if args.subcommand == "version":
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
                systemApiHelper = SystemApiHelper(user_type="metrics", default_username="metrics")
                systemApiHelper.prometheus_metrics(print_response=True)
            elif apicli_args.apicommand == "system":
                handle_systemapi()
            else:
                print(f"Invalid api command {apicli_args.apicommand}")

    elif args.subcommand == "ledger":
        ledgercli_args = ledgercli.parse_args(sys.argv[2:])
        # ledgercli_args = sync --url --dest
        if ledgercli_args.ledgercommand is None:
            ledgercli.print_help()
        else:
            if ledgercli_args.ledgercommand == "sync":
                logger.info(f"Syncing fullnode ledger {sys.argv[3:]}")
                ledgercli_args.func(ledgercli_args)
            else:
                logger.info(f"Invalid ledger command {ledgercli_args.ledgercommand}")

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
    elif args.subcommand in ["version", "optimise-node"]:
        other_command_cli_args = other_command_cli.parse_args(sys.argv[1:])
        if sys.argv[2:] == "-h":
            other_command_cli.print_help()
        other_command_cli_args.func(other_command_cli_args)

    else:
        logger.info(f"Invalid subcommand {args.subcommand}")


if __name__ == "__main__":
    main()
