import unittest
from io import StringIO
from unittest.mock import patch

import urllib3

from babylonnode import main
from config.DockerConfig import DockerConfig
from setup.DockerSetup import DockerSetup
from setup.MigrationSetup import MigrationSetup


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
                                                  './',
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
                       ["main", "docker", "config", "-m", "DETAILED", "-k", "radix", "-nk", "-a", "-d",
                        "/tmp"]):
                main()

            docker_config: DockerConfig = DockerSetup.load_settings("/tmp/config.yaml")
            self.assertEqual("radix", docker_config.core_node.keydetails.keystore_password)

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

    def test_docker_genesis_file_mount_optional_positive(self):
        self.maxDiff = None
        settings = DockerConfig({})
        settings.core_node.core_release = "test"
        settings.common_config.nginx_settings.release = "test"
        settings.common_config.genesis_bin_data_file = '/tmp/genesis.bin'
        docker_compose_yaml = DockerSetup.render_docker_compose(settings)
        self.assertTrue(
            '/tmp/genesis.bin:/home/radixdlt/genesis_data_file.bin' in docker_compose_yaml["services"]["core"][
                "volumes"])

        self.assertEqual("/home/radixdlt/genesis_data_file.bin", docker_compose_yaml["services"]["core"][
            "environment"]["RADIXDLT_GENESIS_DATA_FILE"])

    def test_docker_genesis_file_mount_optional_negative(self):
        self.maxDiff = None
        settings = DockerConfig({})
        settings.core_node.core_release = "test"
        settings.common_config.nginx_settings.release = "test"
        settings.common_config.genesis_bin_data_file = ''
        docker_compose_yaml = DockerSetup.render_docker_compose(settings)
        self.assertFalse(
            '/tmp/genesis.bin:/home/radixdlt/genesis_data_file.bin' in docker_compose_yaml["services"]["core"][
                "volumes"])
        for volume in docker_compose_yaml["services"]["core"]["volumes"]:
            self.assertNotRegex(volume, '.*:/home/radixdlt/genesis_data_file.bin')
        self.assertEqual(None, docker_compose_yaml["services"]["core"][
            "environment"].get("RADIXDLT_GENESIS_DATA_FILE"))

    def test_docker_java_opts_normal_not_on_migration(self):
        self.maxDiff = None
        settings = DockerConfig({})
        settings.core_node.core_release = "test"
        settings.common_config.nginx_settings.release = "test"
        docker_compose_yaml = DockerSetup.render_docker_compose(settings)
        java_opts = docker_compose_yaml["services"]["core"]["environment"]["JAVA_OPTS"]
        self.assertRegex(java_opts, '.*-Xms8g -Xmx8g.*')

    def test_docker_java_opts_increased_on_migration(self):
        self.maxDiff = None
        settings = DockerConfig({})
        settings.core_node.core_release = "test"
        settings.common_config.nginx_settings.release = "test"
        settings = MigrationSetup.ask_migration_config(settings, "someurl",
                                                       "someuser",
                                                       "somepassword",
                                                       "somebech32address")
        docker_compose_yaml = DockerSetup.render_docker_compose(settings)
        java_opts = docker_compose_yaml["services"]["core"]["environment"]["JAVA_OPTS"]
        self.assertRegex(java_opts, '.*-Xms16g -Xmx16g.*')


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DockerUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
