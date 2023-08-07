import unittest
from io import StringIO
from unittest.mock import patch

import urllib3

from babylonnode import main
from config.DockerConfig import DockerConfig


class DockerUnitTests(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_docker_config(self, mockout):
        urllib3.disable_warnings()
        # os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/validator_address.yml"
        # PromptFeeder.prompts_feed = PromptFeeder.instance().load_prompt_feeds()
        with patch('builtins.input', side_effect=['S', 'N', 'N', '/home/runner/docker-compose.yml', 'N']):
            with patch("sys.argv",
                       ["main", "docker", "config", "-m", "DETAILED", "-k", "radix", "-nk", "-a"]):
                main()

    @patch('sys.stdout', new_callable=StringIO)
    def test_docker_config_all_local(self, mockout):
        urllib3.disable_warnings()
        # os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/validator_address.yml"
        # PromptFeeder.prompts_feed = PromptFeeder.instance().load_prompt_feeds()
        with open('/tmp/genesis.json', 'w') as fp:
            pass
        with patch('builtins.input', side_effect=['34',
                                                  '/tmp/genesis.json',
                                                  'Y',
                                                  'Y',
                                                  'radix://node_tdx_22_1qvsml9pe32rzcrmw6jx204gjeng09adzkqqfz0ewhxwmjsaas99jzrje4u3@34.243.93.185',
                                                  'N',
                                                  'Y',
                                                  '/tmp/babylon-node-config',
                                                  'node-keystore.ks',
                                                  '/tmp/data',
                                                  'true',
                                                  'true',
                                                  'Y',
                                                  '',  # remote ip of full node
                                                  'Core',
                                                  'local',
                                                  'postgres',
                                                  'radix-ledger',
                                                  'pgpassword',
                                                  'dataaggregation-version',
                                                  'database-migration-version',
                                                  'gateway-api-version',
                                                  'Y',
                                                  'nginx-version']):
            with patch("sys.argv",
                       ["main", "docker", "config", "-m", "DETAILED", "-k", "radix", "-nk", "-a"]):
                main()

    # @patch('sys.stdout', new_callable=StringIO)
    # def test_docker_config2(self, mockout):
    #     config = Docker.load_settings("/tmp/config.yaml")
    #     self.assertEqual("",config.to_yaml())

    def test_docker_settings_roundtrip(self):
        self.maxDiff = None
        settings = DockerConfig({})
        to_dict = settings.to_dict()
        new_settings = DockerConfig(to_dict)
        self.assertEqual(settings.to_yaml(), new_settings.to_yaml())
        self.assertEqual(settings.to_dict(), new_settings.to_dict())

    @patch('sys.stdout', new_callable=StringIO)
    def test_docker_config(self, mockout):
        urllib3.disable_warnings()
        # os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/validator_address.yml"
        # PromptFeeder.prompts_feed = PromptFeeder.instance().load_prompt_feeds()
        with patch('builtins.input',
                   side_effect=['S', 'N', 'N', '/home/runner/docker-compose.yml', 'N', 'development-latest']):
            with patch("sys.argv",
                       ["main", "docker", "config", "-m", "DETAILED", "-k", "radix", "-nk", "-a"]):
                main()


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DockerUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
