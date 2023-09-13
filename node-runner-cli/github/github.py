import json

import sys
from os import getenv

import requests
from config.EnvVars import (
    RADIXDLT_APP_VERSION_OVERRIDE,
    RADIXDLT_NGINX_VERSION_OVERRIDE,
    RADIXDLT_CLI_VERSION_OVERRIDE,
    RADIXDLT_GATEWAY_VERSION_OVERRIDE
)
from utils.utils import Helpers

REPOS_ENV_VARS = {
    "radixdlt/babylon-node": RADIXDLT_APP_VERSION_OVERRIDE,
    "radixdlt/radixdlt-nginx": RADIXDLT_NGINX_VERSION_OVERRIDE,
    "radixdlt/babylon-nginx": RADIXDLT_NGINX_VERSION_OVERRIDE,
    "radixdlt/node-runner": RADIXDLT_CLI_VERSION_OVERRIDE,
    "radixdlt/babylon-nodecli": RADIXDLT_CLI_VERSION_OVERRIDE,
    "radixdlt/babylon-gateway": RADIXDLT_GATEWAY_VERSION_OVERRIDE,
    "radixdlt/radixdlt-network-gateway": RADIXDLT_GATEWAY_VERSION_OVERRIDE
}


def get_version_override(repo_name: str) -> str:
    return REPOS_ENV_VARS.get(repo_name, None)


def latest_release(repo_name="radixdlt/babylon-node") -> str:
    version_override_env_var = get_version_override(repo_name)
    if version_override_env_var:
        version_override = getenv(version_override_env_var, None)
        if version_override is not None:
            return version_override

    req = requests.Request('GET',
                           f'https://api.github.com/repos/{repo_name}/releases/latest')

    token = getenv('GITHUB_TOKEN')
    prepared = req.prepare()
    prepared.headers['Content-Type'] = 'application/json'
    prepared.headers['user-agent'] = 'babylonnode-cli'
    if token is not None:
        prepared.headers['Authorization'] = f'token {token}'
    resp = Helpers.send_request(prepared, print_response=False)
    if not resp.ok:
        print("Failed to get latest release from github. The response was:")
        print(f"https://api.github.com/repos/{repo_name}/releases/latest")
        print(f"HTTP Code: {resp.status_code}")
        print("Exitting the command...")
        sys.exit(1)

    json_response = json.loads(resp.content)
    return json_response["tag_name"]
