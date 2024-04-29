import ipaddress
import sys

from config.BaseConfig import SetupMode
from github.github import latest_release


class SystemDConfigArguments:
    setupmode: SetupMode
    trustednode: str
    keystore_password: str
    nginx_on_core: str
    data_directory: str
    new_keystore: str
    olympia_node_url: str
    olympia_node_bech32_address: str
    olympia_node_auth_user: str
    olympia_node_auth_password: str
    release: str
    config_file: str
    networkid: str
    hostip: str
    validator: str
    auto_approve: bool

    def __init__(self, args):
        validate_ip(args.hostip)
        self.hostip = args.hostip
        self.setupmode = SetupMode.instance()
        self.setupmode.mode = args.setupmode
        self.trustednode = args.trustednode if args.trustednode != "" else None
        self.keystore_password = (
            args.keystorepassword if args.keystorepassword != "" else None
        )
        self.nginx_on_core = (
            args.disablenginxforcore if args.disablenginxforcore != "" else None
        )
        self.data_directory = args.data_directory
        self.new_keystore = args.newkeystore
        self.olympia_node_url = args.migration_url
        self.olympia_node_bech32_address = args.migration_bech_address
        self.olympia_node_auth_user = args.migration_auth_user
        self.olympia_node_auth_password = args.migration_auth_password
        self.release = args.release if args.release is not None else latest_release()
        self.config_file = f"{args.configdir}/config.yaml"
        self.networkid = args.networkid
        self.validator = args.validator
        self.auto_approve = args.autoapprove


def validate_ip(hostip: str):
    if hostip:
        try:
            ipaddress.ip_address(hostip)
        except ValueError:
            print(f"'{hostip}' is not a valid ip address.")
            sys.exit(1)
