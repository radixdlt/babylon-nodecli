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
                       ["main", "docker", "config", "-m", "DETAILED", "-k", "radix", "-nk", "-a"]):
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
            settings.create_default_config()
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
            render_template = Renderer().load_file_based_template("systemd-default.config.j2").render(
                dict(settings)).rendered
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

    @patch('sys.stdout', new_callable=StringIO)
    def test_systemd_service_file_jinja(self, mockout):
        settings = SystemDSettings({})
        settings.core_node.node_dir = "/nodedir"
        settings.core_node.node_secrets_dir = "/nodedir/secrets"
        settings.core_node.core_release = "1.1.0"

        render_template = Renderer().load_file_based_template("systemd.service.j2").render(dict(settings)).rendered
        fixture = f"""[Unit]
Description=Radix DLT Validator
After=local-fs.target
After=network-online.target
After=nss-lookup.target
After=time-sync.target
After=systemd-journald-dev-log.socket
Wants=network-online.target

[Service]
EnvironmentFile=/nodedir/secrets/environment
User=radixdlt
LimitNOFILE=65536
LimitNPROC=65536
LimitMEMLOCK=infinity
WorkingDirectory=/nodedir
ExecStart=/nodedir/1.1.0/bin/core
SuccessExitStatus=143
TimeoutStopSec=10
Restart=on-failure

[Install]
WantedBy=multi-user.target"""
        self.maxDiff = None
        self.assertEqual(render_template, fixture)

    @patch('sys.stdout', new_callable=StringIO)
    def test_systemd_service_file_jinja(self, mockout):
        settings = SystemDSettings({})
        settings.core_node.keydetails.keystore_password = "nowthatyouknowmysecretiwillfollowyouuntilyouforgetit"

        render_template = Renderer().load_file_based_template("systemd-environment.j2").render(dict(settings.core_node.keydetails)).rendered
        fixture = f"""JAVA_OPTS="--enable-preview -server -Xms8g -Xmx8g  -XX:MaxDirectMemorySize=2048m -XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts -Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom -DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"
RADIX_NODE_KEYSTORE_PASSWORD=nowthatyouknowmysecretiwillfollowyouuntilyouforgetit"""
        self.maxDiff = None
        self.assertEqual(render_template, fixture)

def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
