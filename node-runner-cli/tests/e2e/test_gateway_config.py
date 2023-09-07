import os
import sys
from hashlib import md5
from os import remove
from os.path import dirname, abspath, join, isfile, exists

import pytest
import babylonnode
from utils.PromptFeeder import PromptFeeder


@pytest.fixture
def docker_config_gateway():
    original_argv = sys.argv.copy()
    sys.argv = ["placeholder", "docker", "config", "-m", "GATEWAY", "-d" "/tmp", "-k", "test", "-nk", "-a"]
    yield
    sys.argv = original_argv


@pytest.fixture
def set_gateway_responses():
    root_dir = dirname(dirname(dirname(abspath(__file__))))
    os.environ["PROMPT_FEEDS"] = join(root_dir, "test-prompts/gateway.yml")
    os.environ["GENESIS_SOURCE_PATH"] = join(root_dir, "testnet-genesis", "zabanet_genesis_data_file.bin")
    os.environ["GENESIS_PATH"] = join("/tmp", "genesis.bin")
    os.environ["FORCE_LOAD_FEEDS"] = "true"
    yield
    os.unsetenv("PROMPT_FEEDS")
    os.unsetenv("GENESIS_SOURCE_PATH")
    os.unsetenv("GENESIS_PATH")
    os.unsetenv("FORCE_LOAD_FEEDS")


def test_gateway_config(docker_config_gateway, set_gateway_responses):
    if exists("/tmp/config.yaml"):
        remove("/tmp/config.yaml")

    PromptFeeder.__del__()
    babylonnode.main()
    configs_dir = join(dirname(abspath(__file__)), "configs")

    assert isfile("/tmp/config.yaml")

    # TODO load the file itself and check that the mandatory values are there
    # generated_config = md5(open('/tmp/config.yaml', 'rb').read()).hexdigest()
    # expected_config = md5(open(join(configs_dir, 'expected', 'gateway_config.yml'), 'rb').read()).hexdigest()
    # assert generated_config == expected_config