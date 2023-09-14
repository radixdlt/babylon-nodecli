from argparse import ArgumentParser

from commands.subcommand import get_decorator
from setup.BaseSetup import BaseSetup
from utils.utils import Helpers

other_command_cli = ArgumentParser(
    description='Other CLI commands')
other_command_parser = other_command_cli.add_subparsers(dest="othercommands")


def othercommands(args=[], parent=other_command_parser):
    return get_decorator(args, parent)


@othercommands()
def version(args):
    """
    Run this command td display the version of CLI been used.
    """
    print(f"Cli - Version : {Helpers.cli_version()}")


@othercommands()
def optimise_node(args):
    """
    Run this command to setup ulimits and swap size on the fresh ubuntu machine

    . Prompts asking to setup limits
    . Prompts asking to setup swap and size of swap in GB
    """
    BaseSetup.setup_node_optimisation_config(Helpers.cli_version())


# @othercommands()
# def sync_status(args):
#     """
#     Run this command to see the sync status visualized
#     """
#     user_type = "admin"
#     default_username = "admin"
#     node_host = API.get_host_info()
#     api_client: CustomAPIClient = CustomAPIClient(host=node_host, verify_ssl=False)
#     api_client = SystemApiHelper.set_basic_auth(api_client, user_type, default_username)
#     api_client.prepare("GET", "/system/network-sync-status")
#
#     response_json = Helpers.send_request(api_client.prepared_req, print_request=False, print_response=False)
#     current = int(response_json["sync_status"]["current_state_version"])
#     target = int(response_json["sync_status"]["target_state_version"])
#     pbar = tqdm(total=target)
#     while current < target:
#         sleep(1)
#         response_json = Helpers.send_request(api_client.prepared_req, print_request=False, print_response=False)
#         current = int(response_json["sync_status"]["current_state_version"])
#         pbar.update(current)
#     pbar.close()

