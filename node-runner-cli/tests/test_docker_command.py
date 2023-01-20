import os
import unittest
from unittest.mock import patch

from radixnode import main


class DockerCommandTests(unittest.TestCase):
    def test_docker_config_core(capsys):
        os.environ['PROMPT_FEEDS'] = "test-prompts/core-gateway-all-local.yml"
        with patch("sys.argv", ["main", "docker", "config", "-m", "DETAILED", "-k", "dummypassword", "-a", "-nk"]):
            main()



if __name__ == '__main__':
    unittest.main(warnings='ignore')