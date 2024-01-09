from argparse import ArgumentParser, RawTextHelpFormatter
from commands.subcommand import get_decorator, argument
from ret.accounts import (
    derive_address,
    derive_babylon_address_from_olympia_account_address,
)

ret_cli = ArgumentParser(
    description="Subcommand to help use the Radix Engine Toolkit aka RET",
    usage="babylonnode ret ",
    formatter_class=RawTextHelpFormatter,
)
ret_parser = ret_cli.add_subparsers(dest="retcommand")


def retcommand(args=[], parent=ret_parser):
    return get_decorator(args, parent)


@retcommand(
    [
        argument(
            "-k", "--keystore", required=True, help="Keystore path", action="store"
        ),
        argument(
            "-p", "--password", required=True, help="Keystore password", action="store"
        ),
        argument("-n", "--network", required=True, help="Network id", action="store"),
    ]
)
def derive(args):
    """
    Derive a babylon address from a private key.
    """
    address = derive_address(args.keystore, args.password, int(args.network))
    print(address.address_string())


@retcommand(
    [
        argument(
            "-oa",
            "--olympia-address",
            required=True,
            help="Olympia address",
            action="store",
        ),
        argument(
            "-n",
            "--network",
            required=True,
            help="Network id. Int format",
            action="store",
        ),
    ]
)
def derive_from_olympia(args):
    """
    Derive a babylon address from a private key.
    """
    print(
        derive_babylon_address_from_olympia_account_address(
            args.olympia_address, int(args.network)
        )
    )
