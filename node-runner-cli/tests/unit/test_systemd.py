import os
import re
import unittest
from io import StringIO
from os.path import dirname, join
from pathlib import Path
from unittest.mock import patch

import responses
import urllib3

from babylonnode import main
from config.CommonSystemDConfig import CommonSystemdConfig
from config.CoreSystemDConfig import CoreSystemdConfig
from config.KeyDetails import KeyDetails
from config.Renderer import Renderer
from config.SystemDConfig import SystemDConfig
from setup.MigrationSetup import MigrationSetup
from setup.SystemDSetup import SystemDSetup
from utils.PromptFeeder import PromptFeeder


def file_contains_regular_expression(re_str: str, file: str) -> bool:
    reg = re.compile(re_str)
    with open(file) as f:
        for num, line in enumerate(f, 1):
            regular_expression_find = re.search(reg, line)
            if regular_expression_find:
                return True
    return False


class SystemdUnitTests(unittest.TestCase):
    @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_systemd_install_continue_prompt_feed(self):
        os.environ["PROMPT_FEEDS"] = (
            "test-prompts/individual-prompts/systemd_install_continue.yml"
        )
        PromptFeeder.instance().load_prompt_feeds()
        SystemDSetup.confirm_config("dummy1", "dummy2", "dummy3", "dummy4")

    @unittest.skip("Can only be executed on Ubuntu")
    def test_systemd_config_can_run_without_prompt(self):
        with patch(
            "sys.argv",
            [
                "main",
                "systemd",
                "config",
                "-a",
                "-t",
                "somenode",
                "-i",
                "123.123.123.123",
                "-k",
                "password",
                "-n",
                "S",
                "-d",
                "/tmp/config",
                "-dd",
                "/tmp/babylon-ledger",
            ],
        ):
            main()

    def test_systemd_config_can_be_saved_and_restored_as_yaml(self):
        # Make Python Class YAML Serializable
        config = SystemDConfig({})
        home_directory = Path.home()
        config.core_node.node_dir = "/somedir/babylon-node"
        config.core_node.node_secrets_dir = "/somedir/babylon-node/secret"
        config.migration.use_olympia = True
        key_details = KeyDetails({})
        config.core_node.keydetails = key_details
        config.common_config.host_ip = "6.6.6.6"

        config_file = f"/tmp/config.yaml"
        # with patch('builtins.input', side_effect=['Y']):
        config.to_file(config_file)
        key_details.to_file("/tmp/other")
        # SystemDSetup.save_config(config, config_file)

        self.maxDiff = None
        new_config = SystemDSetup.load_settings(config_file)
        self.assertEqual(new_config.to_yaml(), config.to_yaml())
        self.assertEqual("/somedir/babylon-node", config.core_node.node_dir)
        self.assertEqual(type(config), type(new_config))
        self.assertEqual("/somedir/babylon-node", new_config.core_node.node_dir)

    @unittest.skip("Can only be executed on Ubuntu")
    def test_systemd_dependencies(self):
        with patch("sys.argv", ["main", "systemd", "dependencies"]):
            main()

    @responses.activate
    @patch("sys.stdout", new_callable=StringIO)
    def test_systemd_config(self, mockout):
        urllib3.disable_warnings()
        responses.add(
            responses.GET,
            f"https://ghproxy.radixdlt.com/radixdlt/babylon-nodecli",
            json={"tag_name": "v1"},
            status=200,
        )
        responses.add(
            responses.GET,
            f"https://ghproxy.radixdlt.com/radixdlt/babylon-nginx",
            json={"tag_name": "v1"},
            status=200,
        )
        with patch("builtins.input", side_effect=["Y"]):
            with patch(
                "sys.argv",
                [
                    "main",
                    "systemd",
                    "config",
                    "-m",
                    "CORE",
                    "-i",
                    "18.133.170.30",
                    "-t",
                    "radix://tn1q28eygvxshszxk48jhjxdmyne06m3x6hfyvxg7a45qt8cksffx6z7uu6392@15.236.228.96",
                    "-n",
                    "2",
                    "-k",
                    "radix",
                    "-d",
                    "/tmp",
                    "-dd",
                    "/tmp",
                    "-v",
                    "randomvalidatoraddress",
                    "-nk",
                    "-a",
                    "-r",
                    "1",
                ],
            ):
                main()

    @unittest.skip("For verification only")
    def test_systemd_install_manual(self):
        with patch(
            "sys.argv",
            [
                "main",
                "systemd",
                "install",
                "-a",
                "-m",
                "-f",
                "/tmp/babylon-node/test-config.yaml",
            ],
        ):
            main()

    @patch("sys.stdout", new_callable=StringIO)
    def test_systemd_setup_default_config(self, mockout):
        with patch("builtins.input", side_effect=[]):
            config = SystemDConfig({})
            config.common_config.host_ip = "1.1.1.1"
            config.common_config.network_id = 1
            config.core_node.keydetails.keyfile_path = (
                "/home/radixdlt/babylon-node-config"
            )
            config.core_node.keydetails.keyfile_name = "node-keystore.ks"
            config.core_node.trusted_node = "someNode"
            config.core_node.validator_address = "validatorAddress"
            config.core_node.node_dir = "/tmp"
            config.migration.use_olympia = False
            config.create_default_config_file("")
        self.assertTrue(os.path.isfile("/tmp/default.config"))

        f = open("/tmp/default.config", "r")
        default_config = f.read()
        fixture = """# WARNING!! This file is automatically generated and it is
# overriden when on install/update commands.
# Please consider re-running config/install commands rather
# than manually edit this file

ntp=false
ntp.pool=pool.ntp.org
network.id=1

node.key.path=/home/radixdlt/babylon-node-config/node-keystore.ks
node.key.create_if_missing=true

network.p2p.broadcast_port=30000
network.p2p.listen_port=30001
network.p2p.seed_nodes=someNode
network.p2p.use_proxy_protocol=false
network.host_ip=1.1.1.1

log.level=debug

api.port=3333
api.transactions.enable=true
api.sign.enable=true
api.bind.address=0.0.0.0

api.system.port=3334
api.system.bind_address=0.0.0.0

db.location=/home/radixdlt/babylon-ledger

consensus.validator_address=validatorAddress"""
        self.maxDiff = None
        print(fixture)
        self.assertEqual(fixture.strip(), default_config.strip())

    @patch("sys.stdout", new_callable=StringIO)
    def test_systemd_setup_default_config_without_validator(self, mockout):
        with patch("builtins.input", side_effect=[]):
            settings = SystemDConfig({})
            settings.common_config.host_ip = "1.1.1.1"
            settings.common_config.network_id = 1
            settings.core_node.keydetails.keyfile_path = (
                "/home/radixdlt/babylon-node-config"
            )
            settings.core_node.keydetails.keyfile_name = "node-keystore.ks"
            settings.core_node.trusted_node = "someNode"
            settings.core_node.validator_address = None
            settings.core_node.node_dir = "/tmp"
            settings.create_default_config_file("")
        self.assertTrue(os.path.isfile("/tmp/default.config"))

        f = open("/tmp/default.config", "r")
        default_config = f.read()
        fixture = """ # WARNING!! This file is automatically generated and it is
# overriden when on install/update commands.
# Please consider re-running config/install commands rather
# than manually edit this file

ntp=false
ntp.pool=pool.ntp.org
network.id=1

node.key.path=/home/radixdlt/babylon-node-config/node-keystore.ks
node.key.create_if_missing=true

network.p2p.broadcast_port=30000
network.p2p.listen_port=30001
network.p2p.seed_nodes=someNode
network.p2p.use_proxy_protocol=false
network.host_ip=1.1.1.1

log.level=debug

api.port=3333
api.transactions.enable=true
api.sign.enable=true
api.bind.address=0.0.0.0

api.system.port=3334
api.system.bind_address=0.0.0.0

db.location=/home/radixdlt/babylon-ledger
"""
        self.maxDiff = None
        self.assertEqual(default_config.strip(), fixture.strip())

    @patch("sys.stdout", new_callable=StringIO)
    def test_systemd_setup_default_config_jinja(self, mockout):
        with patch("builtins.input", side_effect=[]):
            settings = SystemDConfig({})
            settings.common_config.genesis_bin_data_file = None
            settings.core_node.keydetails.keyfile_path = (
                "/home/radixdlt/babylon-node-config"
            )
            settings.core_node.keydetails.keyfile_name = "node-keystore.ks"
            settings.core_node.trusted_node = "someNode"
            settings.common_config.host_ip = "1.1.1.1"
            settings.common_config.network_id = 1
            settings.core_node.validator_address = "validatorAddress"
            settings.migration.use_olympia = False
            render_template = (
                Renderer()
                .load_file_based_template("systemd-default.config.j2")
                .render(settings.to_dict())
                .rendered
            )
        fixture = """# WARNING!! This file is automatically generated and it is
# overriden when on install/update commands.
# Please consider re-running config/install commands rather
# than manually edit this file

ntp=false
ntp.pool=pool.ntp.org
network.id=1

node.key.path=/home/radixdlt/babylon-node-config/node-keystore.ks
node.key.create_if_missing=true

network.p2p.broadcast_port=30000
network.p2p.listen_port=30001
network.p2p.seed_nodes=someNode
network.p2p.use_proxy_protocol=false
network.host_ip=1.1.1.1

log.level=debug

api.port=3333
api.transactions.enable=true
api.sign.enable=true
api.bind.address=0.0.0.0

api.system.port=3334
api.system.bind_address=0.0.0.0

db.location=/home/radixdlt/babylon-ledger

consensus.validator_address=validatorAddress

"""
        self.maxDiff = None
        self.assertEqual(fixture.strip(), render_template.strip())

    @patch("sys.stdout", new_callable=StringIO)
    def test_systemd_service_file_jinja(self, mockout):
        settings = SystemDConfig({})
        settings.core_node.node_dir = "/nodedir"
        settings.core_node.node_secrets_dir = "/nodedir/secrets"
        settings.core_node.core_release = "1.1.0"

        render_template = (
            Renderer()
            .load_file_based_template("systemd.service.j2")
            .render(settings.to_dict())
            .rendered
        )
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
WantedBy=multi-user.target

"""
        self.maxDiff = None
        self.assertEqual(render_template, fixture)

    @patch("sys.stdout", new_callable=StringIO)
    def test_systemd_service_file_jinja(self, mockout):
        settings = SystemDConfig({})
        settings.core_node.keydetails = KeyDetails({})
        settings.core_node.keydetails.keystore_password = (
            "nowthatyouknowmysecretiwillfollowyouuntilyouforgetit"
        )
        render_template = (
            Renderer()
            .load_file_based_template("systemd-environment.j2")
            .render(settings.to_dict())
            .rendered
        )
        fixture = f"""JAVA_OPTS="--enable-preview -server -Xms12g -Xmx12g  -XX:MaxDirectMemorySize=2048m -XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts -Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom -DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"
RADIX_NODE_KEYSTORE_PASSWORD=nowthatyouknowmysecretiwillfollowyouuntilyouforgetit"""
        self.maxDiff = None
        self.assertEqual(fixture, render_template)

    def test_systemd_settings_roundtrip(self):
        settings = SystemDConfig({})
        to_dict = settings.to_dict()
        new_settings = SystemDConfig(to_dict)
        self.assertEqual(settings.to_dict(), new_settings.to_dict())
        self.assertEqual(settings.to_yaml(), new_settings.to_yaml())
        settings.to_file("/tmp/tmp.config.yml")
        file_settings = SystemDSetup.load_settings("/tmp/tmp.config.yml")
        self.assertEqual(settings.to_dict(), file_settings.to_dict())
        self.assertEqual(settings.to_yaml(), file_settings.to_yaml())

    def test_systemd_settings_random(self):
        mydict = {"core_node": {"core_release": "3"}}
        self.assertEqual({"core_release": "3"}, mydict.get("core_node"))
        mycoreconf = CoreSystemdConfig(mydict.get("core_node"))
        self.assertEqual("3", mycoreconf.core_release)
        myconf = SystemDConfig(mydict)
        self.assertEqual("3", myconf.core_node.core_release)

    def test_systemd_settings_random2(self):
        test = CommonSystemdConfig({"network_id": 12})
        self.assertEqual(12, test.network_id)

    def test_systemd_settings_random3(self):
        test = CommonSystemdConfig({"network_id": 12})
        self.assertEqual(
            {
                "genesis_bin_data_file": "",
                "host_ip": "",
                "network_id": 12,
                "network_name": "",
                "nginx_settings": {
                    "config_url": "",
                    "dir": "/etc/nginx",
                    "mode": "systemd",
                    "protect_core": "true",
                    "release": "",
                    "secrets_dir": "/etc/nginx/secrets",
                },
                "service_user": "radixdlt",
            },
            test.to_dict(),
        )

    def test_systemd_java_opts_normal_not_on_migration(self):
        self.maxDiff = None
        settings = SystemDConfig({})
        settings.core_node.core_release = "test"
        settings.common_config.nginx_settings.release = "test"
        environment_yaml = settings.create_environment_yaml()
        self.assertTrue("-Xms12g -Xmx12g" in environment_yaml)

    def test_systemd_java_opts_increased_on_migration(self):
        self.maxDiff = None
        settings = SystemDConfig({})
        settings.core_node.core_release = "test"
        settings.common_config.nginx_settings.release = "test"
        settings = MigrationSetup.ask_migration_config(
            settings, "someurl", "someuser", "somepassword", "somebech32address"
        )
        environment_yaml = settings.create_environment_yaml()
        self.assertTrue("-Xms12g -Xmx12g" in environment_yaml)

    @responses.activate
    def test_systemd_version_update(self):
        responses.add(
            responses.GET,
            f"https://ghproxy.radixdlt.com/radixdlt/babylon-node",
            json={"tag_name": "v1"},
            status=200,
        )

        responses.add(
            responses.GET,
            f"https://ghproxy.radixdlt.com/radixdlt/babylon-gateway",
            json={"tag_name": "v1"},
            status=200,
        )

        responses.add(
            responses.GET,
            f"https://ghproxy.radixdlt.com/radixdlt/babylon-nginx",
            json={"tag_name": "v1"},
            status=200,
        )

        systemd_config = SystemDConfig({})
        systemd_config.gateway.enabled = True
        systemd_config.core_node.core_release = "oldversion"
        systemd_config.gateway.gateway_api.release = "oldversion"
        systemd_config.gateway.data_aggregator.release = "oldversion"
        systemd_config.gateway.database_migration.release = "oldversion"
        systemd_config = SystemDSetup.update_versions(systemd_config, True)
        self.assertNotEqual("oldversion", systemd_config.core_node.core_release)
        self.assertNotEqual("oldversion", systemd_config.gateway.gateway_api.release)
        self.assertNotEqual(
            "oldversion", systemd_config.gateway.data_aggregator.release
        )
        self.assertNotEqual(
            "oldversion", systemd_config.gateway.database_migration.release
        )

        del systemd_config.gateway.database_migration
        systemd_config.core_node.core_release = "oldversion"
        systemd_config.gateway.gateway_api.release = "oldversion"
        systemd_config.gateway.data_aggregator.release = "oldversion"
        systemd_config = SystemDSetup.update_versions(systemd_config, True)
        self.assertNotEqual("oldversion", systemd_config.core_node.core_release)
        self.assertNotEqual("oldversion", systemd_config.gateway.gateway_api.release)
        self.assertNotEqual(
            "oldversion", systemd_config.gateway.data_aggregator.release
        )

        del systemd_config.gateway
        systemd_config.core_node.core_release = "oldversion"
        systemd_config = SystemDSetup.update_versions(systemd_config, True)
        self.assertNotEqual("oldversion", systemd_config.core_node.core_release)

    def test_advanced_config_is_added(self):
        settings = SystemDConfig({})
        settings.core_node.node_dir = "/tmp/"
        tests_dir = dirname(dirname(__file__))
        fixture_file = join(tests_dir, "fixtures/advanced-user.default.config")

        settings.create_default_config_file(fixture_file)

        self.assertTrue(os.path.exists("/tmp/default.config"))
        self.assertTrue(
            file_contains_regular_expression(
                "random.other.config=thisconfigdoesnotexist", "/tmp/default.config"
            )
        )


def suite():
    """This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
