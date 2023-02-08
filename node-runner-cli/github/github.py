import json
import os
import sys

import requests

from env_vars import RADIXDLT_APP_VERSION_OVERRIDE, RADIXDLT_NGINX_VERSION_OVERRIDE, RADIXDLT_CLI_VERSION_OVERRIDE, \
    RADIXDLT_GATEWAY_VERSION_OVERRIDE
from utils.utils import Helpers


def latest_release(repo_name="radixdlt/babylon-node"):
    if repo_name == "radixdlt/babylon-node":
        if os.environ.get(RADIXDLT_APP_VERSION_OVERRIDE) is not None:
            return os.environ.get(RADIXDLT_APP_VERSION_OVERRIDE)

    if repo_name == "radixdlt/radixdlt-nginx" or repo_name == "radixdlt/babylon-nginx":
        if os.environ.get(RADIXDLT_NGINX_VERSION_OVERRIDE) is not None:
            return os.environ.get(RADIXDLT_NGINX_VERSION_OVERRIDE)

    if repo_name == "radixdlt/node-runner" or repo_name == "radixdlt/babylon-nodecli":
        if os.environ.get(RADIXDLT_CLI_VERSION_OVERRIDE) is not None:
            return os.environ.get(RADIXDLT_CLI_VERSION_OVERRIDE)

    if repo_name == "radixdlt/babylon-gateway" or repo_name == "radixdlt/radixdlt-network-gateway":
        if os.environ.get(RADIXDLT_GATEWAY_VERSION_OVERRIDE):
            return os.environ.get(RADIXDLT_GATEWAY_VERSION_OVERRIDE)

    req = requests.Request('GET',
                           f'https://api.github.com/repos/{repo_name}/releases/latest')

    token = os.getenv('GITHUB_TOKEN')
    prepared = req.prepare()
    prepared.headers['Content-Type'] = 'application/json'
    prepared.headers['user-agent'] = 'radixnode-cli'
    if token is not None:
        prepared.headers['Authorization'] = token
    resp = Helpers.send_request(prepared, print_response=False)
    if not resp.ok:
        print("Failed to get latest release from github. The response was:")
        print(f"https://api.github.com/repos/{repo_name}/releases/latest")
        print(f"HTTP Code: {resp.status_code}")
        print("Exitting the command...")
        sys.exit(1)

    json_response = json.loads(resp.content)
    return json_response["tag_name"]
