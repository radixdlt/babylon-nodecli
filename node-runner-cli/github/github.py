import json
import os
import sys

import requests
from utils.utils import Helpers


def latest_release(repo_name="radixdlt/radixdlt"):
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
        sys.exit()

    json_response = json.loads(resp.content)
    return json_response["tag_name"]
