import json
import os
import sys

import requests
from utils.utils import Helpers


def latest_release(repo_name="radixdlt/radixdlt"):
    if repo_name == "radixdlt/babylon-nginx":
        return os.environ.get('RADIXDTL_OVERRIDE_NGINX_VERSION')
    if repo_name == "radixdlt/babylon-nodecli":
        return os.environ.get('RADIXDTL_OVERRIDE_CLI_VERSION')
    if repo_name == "radixdlt/babylon-gateway":
        return os.environ.get('RADIXDTL_OVERRIDE_GATEWAY_VERSION')

    token = os.environ.get('GITHUB_TOKEN', 'token notvalid')
    req = requests.Request('GET',
                           f'https://api.github.com/repos/{repo_name}/releases/latest')

    prepared = req.prepare()
    prepared.headers['Content-Type'] = 'application/json'
    prepared.headers['user-agent'] = 'radixnode-cli'
    prepared.headers['Authorization'] = token
    resp = Helpers.send_request(prepared, print_response=False)
    if not resp.ok:
        print("Failed to get latest release from github. Exitting the command...")
        sys.exit()

    json_response = json.loads(resp.content)
    return json_response["tag_name"]
