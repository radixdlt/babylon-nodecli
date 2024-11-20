from os import getenv

from config.BaseConfig import SetupMode
from github.github import latest_release


class DockerConfigArguments:
    setupmode: SetupMode
    trustednode: str
    keystore_password: str
    postgrespassword: str
    validator: str
    olympia_node_url: str
    olympia_node_bech32_address: str
    olympia_node_auth_user: str
    olympia_node_auth_password: str
    release: str
    nginx_on_core: bool
    nginx_on_gateway: bool
    autoapprove: bool
    new_keystore: bool
    config_file: str
    networkid: str
    download_community_snapshot: bool

    def __init__(self, args):
        self.setupmode = SetupMode.instance()
        self.setupmode.mode = args.setupmode
        self.trustednode = args.trustednode if args.trustednode != "" else None
        self.keystore_password = (
            args.keystorepassword if args.keystorepassword != "" else None
        )
        self.nginx_on_core = (
            args.disablenginxforcore if args.disablenginxforcore != "" else None
        )
        self.nginx_on_gateway = (
            args.disablenginxforgateway if args.disablenginxforgateway != "" else None
        )
        self.postgrespassword = (
            args.postgrespassword if args.postgrespassword != "" else None
        )
        self.autoapprove = args.autoapprove
        self.new_keystore = args.newkeystore
        self.validator = args.validator
        self.olympia_node_url = args.migration_url
        self.olympia_node_bech32_address = args.migration_bech_address
        self.olympia_node_auth_user = args.migration_auth_user
        self.olympia_node_auth_password = args.migration_auth_password
        self.release = getenv("LATEST_RELEASE", latest_release())
        self.config_file = f"{args.configdir}/config.yaml"
        self.networkid = args.networkid
        self.download_community_snapshot = args.download_community_snapshot


class DockerInstallArguments:
    autoapprove: bool
    config_file: str
    update: bool

    def __init__(self, args):
        self.autoapprove = args.autoapprove
        self.config_file = args.configfile
        self.update = args.update
