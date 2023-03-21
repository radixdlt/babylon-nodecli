import os
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from config.KeyDetails import KeyDetails
from config.Renderer import Renderer
from config.SystemDConfig import SystemDSettings
from radixnode import main
from setup.SystemD import SystemD
from utils.PromptFeeder import PromptFeeder
from utils.utils import Helpers


class SystemdUnitTests(unittest.TestCase):

    @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_systemd_install_continue_prompt_feed(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_continue.yml"
        PromptFeeder.instance().load_prompt_feeds()
        SystemD.confirm_config("dummy1", "dummy2", "dummy3", "dummy4")

    @unittest.skip("Can only be executed on Ubuntu")
    def test_systemd_install_sets_environments_by_creating_file(self):
        SystemD.set_environment_variables("dummypw", "/tmp")
        self.assertTrue(os.path.isfile("/tmp/environment"))

    @unittest.skip("Can only be executed on Ubuntu")
    def test_systemd_creates_default_config_without_asking(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_default_config.yml"
        PromptFeeder.instance().load_prompt_feeds()
        SystemD.setup_default_config("radix:12345dummynode", "1.1.1.1", "/tmp", "???", "false")
        self.assertTrue(os.path.isfile("/tmp/default.config"))
        # ToDo: Test Appending of override lines

    @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_systemd_creates_service_file_without_asking(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_default_config.yml"
        PromptFeeder.instance().load_prompt_feeds()
        PromptFeeder.instance()
        SystemD.setup_service_file("someversion", "/tmp", "/tmp/secrets", "/tmp/servicefile")
        self.assertTrue(os.path.isfile("/tmp/servicefile"))

    @unittest.skip("Can only be executed on Ubuntu")
    def test_systemd_config_can_run_without_prompt(self):
        with patch("sys.argv",
                   ["main", "systemd", "config",
                    "-a",
                    "-t", "somenode",
                    "-i", "123.123.123.123",
                    "-k", "password",
                    "-n", "S",
                    "-d", "/tmp/config",
                    "-dd", "/tmp/data"]):
            main()

    def test_systemd_config_can_be_saved_and_restored_as_yaml(self):
        # Make Python Class YAML Serializable
        settings = SystemDSettings({})
        home_directory = Path.home()
        settings.core_node.node_dir = "/somedir/node-config"
        settings.core_node.node_secrets_dir = "/somedir/node-config/secret"
        key_details = KeyDetails({})
        settings.core_node.keydetails = key_details
        settings.common_config.host_ip = "6.6.6.6"

        config_file = f"/tmp/config.yaml"
        with patch('builtins.input', side_effect=['Y']):
            SystemD.save_settings(settings, config_file)

        self.maxDiff = None
        new_settings = SystemD.load_settings(config_file)
        self.assertEqual(new_settings.to_yaml(), settings.to_yaml())
        self.assertEqual(new_settings.core_node.node_dir, "/somedir/node-config")

    @unittest.skip("Can only be executed on Ubuntu")
    def test_systemd_dependencies(self):
        with patch("sys.argv",
                   ["main", "systemd", "dependencies"]):
            main()

    @patch('sys.stdout', new_callable=StringIO)
    def test_systemd_config(self, mockout):
        with patch('builtins.input', side_effect=['Y']):
            with patch("sys.argv",
                       ["main", "systemd", "config", "-m", "CORE", "-i", "18.133.170.30", "-t",
                        "radix://tn1q28eygvxshszxk48jhjxdmyne06m3x6hfyvxg7a45qt8cksffx6z7uu6392@15.236.228.96",
                        "-n", "2", "-k", "radix", "-d", "/tmp", "-dd", "/tmp", "-v", "randomvalidatoraddress", "-a"]):
                main()

    @patch('sys.stdout', new_callable=StringIO)
    def test_docker_config(self, mockout):
        # os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/validator_address.yml"
        # PromptFeeder.prompts_feed = PromptFeeder.instance().load_prompt_feeds()
        with patch('builtins.input', side_effect=['S', 'N', 'N', '/home/runner/docker-compose.yml', 'N']):
            with patch("sys.argv",
                       ["main", "docker", "config", "-m", "DETAILED", "-k", "radix", "-nk","-a"]):
                main()

    @patch('sys.stdout', new_callable=StringIO)
    def test_docker_config_all_local(self, mockout):
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
                                                  '/tmp/node-config',
                                                  'node-keystore.ks',
                                                  '/tmp/data',
                                                  'true',
                                                  'true',
                                                  'development-latest']):
            with patch("sys.argv",
                       ["main", "docker", "config", "-m", "DETAILED", "-k", "radix", "-nk", "-a"]):
                main()

    @unittest.skip("For verification only")
    def test_systemd_install_manual(self):
        with patch("sys.argv",
                   ["main", "systemd", "install", "-a", "-m", "-f", "/tmp/node-config/test-config.yaml"]):
            main()

    @patch('sys.stdout', new_callable=StringIO)
    def test_systemd_setup_default_config(self, mockout):
        with patch('builtins.input', side_effect=['/tmp/genesis.json']):
            settings = SystemDSettings({})
            settings.common_config.host_ip = "1.1.1.1"
            settings.common_config.network_id = 34
            settings.core_node.keydetails.keyfile_path = "/tmp/node-config"
            settings.core_node.keydetails.keyfile_name = "node-keystore.ks"
            settings.core_node.trusted_node = "someNode"
            settings.core_node.validator_address = "validatorAddress"
            settings.core_node.node_dir = "/tmp"
            SystemD.setup_default_config(settings)
        self.assertTrue(os.path.isfile("/tmp/default.config"))

        f = open("/tmp/default.config", "r")
        default_config = f.read()
        fixture = """ntp=false
ntp.pool=pool.ntp.org

network.id=34
network.genesis_file=/tmp/genesis.json

node.key.path=/tmp/node-config/node-keystore.ks

network.p2p.broadcast_port=30000
network.p2p.listen_port=30001
network.p2p.seed_nodes=someNode
network.p2p.use_proxy_protocol=false
network.host_ip=1.1.1.1

log.level=debug

api.port=3334
api.transactions.enable=true
api.sign.enable=true
api.bind.address=0.0.0.0

db.location=/home/radixdlt/data

consensus.validator_address=validatorAddress
"""
        self.maxDiff = None
        self.assertEqual(default_config, fixture)

    @patch('sys.stdout', new_callable=StringIO)
    def test_systemd_setup_default_config_jinja(self, mockout):

        with patch('builtins.input', side_effect=['/tmp/genesis.json']):
            settings = SystemDSettings({})
            settings.common_config.genesis_json_location = None
            settings.core_node.keydetails.keyfile_path = "/tmp/node-config"
            settings.core_node.keydetails.keyfile_name = "node-keystore.ks"
            settings.core_node.trusted_node = "someNode"
            settings.common_config.host_ip = "1.1.1.1"
            settings.common_config.network_id = 1
            settings.core_node.validator_address = "validatorAddress"
            render_template = Renderer().load_file_based_template("systemd-default.config.j2").render(dict(settings)).rendered
        fixture = """ntp=false
ntp.pool=pool.ntp.org

network.id=1

node.key.path=/tmp/node-config/node-keystore.ks

network.p2p.broadcast_port=30000
network.p2p.listen_port=30001
network.p2p.seed_nodes=someNode
network.p2p.use_proxy_protocol=false
network.host_ip=1.1.1.1

log.level=debug

api.port=3334
api.transactions.enable=true
api.sign.enable=true
api.bind.address=0.0.0.0

db.location=/home/radixdlt/data

consensus.validator_address=validatorAddress
"""
        self.maxDiff = None
        self.assertEqual(render_template, fixture)


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
