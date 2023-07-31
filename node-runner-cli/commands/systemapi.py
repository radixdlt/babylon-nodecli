import sys
from argparse import ArgumentParser

from api.SystemApiHelper import SystemApiHelper
from commands.subcommand import get_decorator

systemapicli = ArgumentParser(
    description='Subcommand to aid interaction with system api of core node',
    usage="babylonnode api system ")
systemapi_parser = systemapicli.add_subparsers(dest="systemapicommand")


def handle_systemapi():
    systemcli_args = systemapicli.parse_args(sys.argv[3:])
    if systemcli_args.systemapicommand is None:
        systemapicli.print_help()
    else:
        systemcli_args.func(systemcli_args)


def systemapicommand(args=[], parent=systemapi_parser):
    return get_decorator(args, parent)


@systemapicommand()
def version(args):
    """
    This command displays the version of node software that is currently running
    """
    systemApiHelper = SystemApiHelper()
    systemApiHelper.version(print_response=True)


@systemapicommand()
def health(args):
    """
    This command displays the health of the node on whether it is syncing, or booting or up
    """

    systemApiHelper = SystemApiHelper()
    systemApiHelper.health(print_response=True)


@systemapicommand()
def configuration(args):
    """
    This command displays the configuration of the node
    """

    systemApiHelper = SystemApiHelper()
    systemApiHelper.configuration(print_response=True)


@systemapicommand()
def peers(args):
    """
    This command displays peers that node sees on the network
    """

    systemApiHelper = SystemApiHelper()
    systemApiHelper.peers(print_response=True)


@systemapicommand()
def addressbook(args):
    """
    This command displays address book on the data the node has stored
    """

    systemApiHelper = SystemApiHelper()
    systemApiHelper.addressbook(print_response=True)


@systemapicommand()
def network_sync_status(args):
    """
    This command displays information on the status with respect to syncing to network.
    """
    systemApiHelper = SystemApiHelper()
    systemApiHelper.network_sync_status(print_response=True)


@systemapicommand()
def identity(args):
    """
    This command displays information on the status with respect to syncing to network.
    """
    systemApiHelper = SystemApiHelper()
    systemApiHelper.identity(print_response=True)
