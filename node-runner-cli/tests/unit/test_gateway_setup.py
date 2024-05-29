import unittest
from io import StringIO
from os.path import dirname, join
from pathlib import Path
from unittest.mock import patch

import urllib3
import yaml
from deepdiff import DeepDiff
from yaml import UnsafeLoader

from config.BaseConfig import SetupMode
from config.DockerConfig import DockerConfig
from config.SystemDConfig import SystemDConfig
from setup.DockerSetup import DockerSetup
from setup.GatewaySetup import GatewaySetup
from utils.Prompts import Prompts
from utils.utils import Helpers


class GatewaySetupTests(unittest.TestCase):
    fixture: SystemDConfig = SystemDConfig({})

    @classmethod
    def setUpClass(cls):
        cls.fixture.gateway.enabled = True
        cls.fixture.gateway.gateway_api.coreApiNode.core_api_address = (
            "https://localhost:3332"
        )
        cls.fixture.gateway.gateway_api.coreApiNode.Name = "CoreNode"
        cls.fixture.gateway.gateway_api.coreApiNode.enabled = "True"
        cls.fixture.gateway.gateway_api.coreApiNode.basic_auth_user = "admin"
        cls.fixture.gateway.gateway_api.coreApiNode.basic_auth_password = "radix"
        cls.fixture.gateway.gateway_api.coreApiNode.auth_header = (
            Helpers.get_basic_auth_header_from_user_and_password("admin", "radix")
        )
        cls.fixture.gateway.gateway_api.coreApiNode.disable_core_api_https_certificate_checks = (
            "true"
        )

        cls.fixture.gateway.gateway_api.release = ""
        # cls.fixture.gateway.gateway_api.repo = "radixdlt/gateway-test-dummy"

        cls.fixture.gateway.data_aggregator.coreApiNode = (
            cls.fixture.gateway.gateway_api.coreApiNode
        )
        # cls.fixture.gateway.data_aggregator.release = "testrelease"
        # cls.fixture.gateway.data_aggregator.repo = "radixdlt/gateway-test-dummy"
        cls.fixture.gateway.data_aggregator.NetworkName = "zabanet"

        # cls.fixture.gateway.database_migration.release = "testrelease"
        # cls.fixture.gateway.database_migration.repo = "radixdlt/gateway-test-dummy"

        cls.fixture.gateway.postgres_db.setup = "local"
        cls.fixture.gateway.postgres_db.user = "postgres"
        cls.fixture.gateway.postgres_db.password = "radix"
        cls.fixture.gateway.postgres_db.host = "host.docker.internal:5432"
        cls.fixture.gateway.postgres_db.dbname = "radixdlt_ledger"
        cls.fixture.gateway.docker_compose = "/tmp/gateway.docker-compose.yml"

    # @patch('sys.stdout', new_callable=StringIO)
    # def test_setup_gateway_generate_compose_file(self, mockout):
    #     urllib3.disable_warnings()
    #     with patch('builtins.input', side_effect=['n']):
    #         GatewaySetup.install_standalone_gateway(self.fixture)
    #         docker_compose_string = self.read_compose_file_from_disc()
    #         self.assertEqual(self.render_compose_fixture(), docker_compose_string.strip())

    def read_compose_file_from_disc(self):
        docker_compose_file_path = self.fixture.gateway.docker_compose
        docker_compose_file = Path(docker_compose_file_path)
        self.assertTrue(docker_compose_file.is_file())
        f = open(docker_compose_file, "r")
        docker_compose_string = f.read()
        return docker_compose_string

    def render_compose_fixture(self):
        return f"""version: '2.4'
services:
  gateway_api: # This is the base -- the _image and _built containers are defined below
    image: {self.fixture.gateway.gateway_api.repo}:{self.fixture.gateway.gateway_api.release}
    ports:
      - "127.0.0.1:5207:80" # This allows you to connect to the API at http://localhost:5308
      - "127.0.0.1:1235:1235" # This allows you to connect to the metrics API at http://localhost:1235
    restart: unless-stopped
    extra_hosts:
    - "host.docker.internal:host-gateway"
    environment:
      ASPNETCORE_URLS: "http://*:80" # Binds to 80 on all interfaces
      PrometheusMetricsPort: "1235"
      EnableSwagger: "true"
      ConnectionStrings__NetworkGatewayReadOnly: "Host={self.fixture.gateway.postgres_db.host};Database={self.fixture.gateway.postgres_db.dbname};Username={self.fixture.gateway.postgres_db.user};Password={self.fixture.gateway.postgres_db.password}"
      ConnectionStrings__NetworkGatewayReadWrite: "Host={self.fixture.gateway.postgres_db.host};Database={self.fixture.gateway.postgres_db.dbname};Username={self.fixture.gateway.postgres_db.user};Password={self.fixture.gateway.postgres_db.password}"
      GatewayApi__Endpoints_MaxPageSize: "30"
      # GatewayApi__MaxWaitForDbOnStartupMs: "90" # Wait for PostGres to boot up
      GatewayApi__Network__DisableCoreApiHttpsCertificateChecks: "false"
      GatewayApi__Network__NetworkName: ""
      GatewayApi__Network__CoreApiNodes__0__Name: "{self.fixture.gateway.data_aggregator.coreApiNode.Name}"
      GatewayApi__Network__CoreApiNodes__0__CoreApiAddress: "{self.fixture.gateway.gateway_api.coreApiNode.core_api_address}"
      GatewayApi__Network__CoreApiNodes__0__CoreApiAuthorizationHeader: '{self.fixture.gateway.gateway_api.coreApiNode.auth_header.Authorization}"
      GatewayApi__Network__CoreApiNodes__0__RequestWeighting: "1"
      GatewayApi__Network__CoreApiNodes__0__Enabled: "{self.fixture.gateway.gateway_api.coreApiNode.enabled}"
  data_aggregator:
    depends_on:
      - database_migrations
    image: {self.fixture.gateway.data_aggregator.repo}:{self.fixture.gateway.data_aggregator.release}
    restart: unless-stopped
    cpus: 2.0
    extra_hosts:
    - "host.docker.internal:host-gateway"
    ports:
      - "127.0.0.1:5208:80" # This allows you to connect to the API (for root and health checks) at http://localhost:5207
      - "127.0.0.1:1234:1234" # This allows you to connect to the metrics API at http://localhost:1234
    environment:
      # WIPE_DATABASE: "true"
      ASPNETCORE_URLS: "http://*:80" # Binds to 80 on all interfaces
      ConnectionStrings__NetworkGatewayReadWrite: "Host={self.fixture.gateway.postgres_db.host};Database={self.fixture.gateway.postgres_db.dbname};Username={self.fixture.gateway.postgres_db.user};Password={self.fixture.gateway.postgres_db.password}"
      PrometheusMetricsPort: "1234"
      #DataAggregator__Network__MaxWaitForDbOnStartupMs: "90"
      DataAggregator__Network__DisableCoreApiHttpsCertificateChecks:  "false"
      DataAggregator__Network__NetworkName: ""
      DataAggregator__Network__CoreApiNodes__0__Name: "{self.fixture.gateway.data_aggregator.coreApiNode.Name}"
      DataAggregator__Network__CoreApiNodes__0__CoreApiAddress: "{self.fixture.gateway.gateway_api.coreApiNode.core_api_address}"
      GatewayApi__Network__CoreApiNodes__0__CoreApiAuthorizationHeader: '{self.fixture.gateway.gateway_api.coreApiNode.auth_header.Authorization}"
      DataAggregator__Network__CoreApiNodes__0__TrustWeighting:  "1"
      DataAggregator__Network__CoreApiNodes__0__Enabled:  "{self.fixture.gateway.gateway_api.coreApiNode.enabled}"
  database_migrations: # This is the base -- the _image and _built containers are defined below
    image: {self.fixture.gateway.database_migration.repo}:{self.fixture.gateway.database_migration.release}
    environment:
      ConnectionStrings__NetworkGatewayMigrations: Host={self.fixture.gateway.postgres_db.host};Database={self.fixture.gateway.postgres_db.dbname};Username={self.fixture.gateway.postgres_db.user};Password={self.fixture.gateway.postgres_db.password}
    extra_hosts:
    - "host.docker.internal:host-gateway" """.strip()

    @patch("sys.stdout", new_callable=StringIO)
    def test_setup_gateway_ask_core_api(self, mockout):
        SetupMode.instance()
        SetupMode.mode = "DETAILED"
        urllib3.disable_warnings()
        keyboard_input = ["", "CoreNodeName"]
        default_value = "http://localhost:3332"
        with patch("builtins.input", side_effect=keyboard_input):
            core_api = GatewaySetup.ask_core_api_node_settings(default_value)

        self.assertEqual(default_value, core_api.core_api_address)
        self.assertEqual("CoreNodeName", core_api.Name)

    @patch("sys.stdout", new_callable=StringIO)
    def test_setup_gateway_get_CoreApiAddress(self, mockout):
        urllib3.disable_warnings()
        # Takes default value
        keyboard_input = ""
        default_value = "http://localhost:3332"
        with patch("builtins.input", side_effect=[keyboard_input]):
            # Core Node Address
            core_api_address = Prompts.get_CoreApiAddress(default_value)

        self.assertEqual(default_value, core_api_address)
        # Overrides with input
        keyboard_input = "http://core:3333/core"
        with patch("builtins.input", side_effect=[keyboard_input]):
            # Core Node Address
            core_api_address = Prompts.get_CoreApiAddress(default_value)
        self.assertEqual(keyboard_input, core_api_address)

    @patch("sys.stdout", new_callable=StringIO)
    def test_setup_gateway_compose_file_fixture_test(self, mockout):
        urllib3.disable_warnings()
        # Takes default values
        questionary_keyboard_input = [
            "https://host.docker.internal:443/core",
            "admin",
            "radix",
            "true",
            "CoreNode",
            "rcnet-v3-r1",
            "rcnet-v3-r1",
            "rcnet-v3-r1",
            "local",
            "radixdlt_ledger",
            "postgres",
        ]
        # Does not start the docker compose file, just generates it
        install_keyboard_input = "n"
        config = SystemDConfig({})

        with patch("builtins.input", side_effect=questionary_keyboard_input):
            config.gateway = GatewaySetup.ask_gateway_standalone_docker("postgres")

        self.assertEqual("postgres", config.gateway.postgres_db.password)

        # Have to manually set this because we skipped systemd setup
        config.common_config.network_name = "zabanet"
        config.gateway.enabled = True

        self.expect_ask_gateway_inputs_get_inserted_into_object(
            config, questionary_keyboard_input
        )
        self.assertEqual("host.docker.internal:5432", config.gateway.postgres_db.host)

        config.gateway.docker_compose = "/tmp/gateway.docker-compose.yml"

        with patch("builtins.input", side_effect=[install_keyboard_input]):
            GatewaySetup.conditionaly_install_standalone_gateway(config)

        tests_dir = dirname(dirname(__file__))
        fixture_file = join(tests_dir, "fixtures/gateway-docker-compose.yaml")
        with open(fixture_file) as f1:
            with open(config.gateway.docker_compose) as f2:
                self.assertEqual(f1.read(), f2.read())

    def expect_ask_gateway_inputs_get_inserted_into_object(
        self, config, questionary_keyboard_input
    ):
        self.assertEqual(
            questionary_keyboard_input[0],
            config.gateway.gateway_api.coreApiNode.core_api_address,
        )
        self.assertEqual(
            questionary_keyboard_input[1],
            config.gateway.gateway_api.coreApiNode.basic_auth_user,
        )
        self.assertEqual(
            questionary_keyboard_input[2],
            config.gateway.gateway_api.coreApiNode.basic_auth_password,
        )
        self.assertEqual(
            questionary_keyboard_input[3],
            config.gateway.gateway_api.coreApiNode.disable_core_api_https_certificate_checks,
        )
        self.assertEqual(
            questionary_keyboard_input[4], config.gateway.gateway_api.coreApiNode.Name
        )
        self.assertEqual(
            questionary_keyboard_input[5], config.gateway.gateway_api.release
        )
        self.assertEqual(
            questionary_keyboard_input[6], config.gateway.data_aggregator.release
        )
        self.assertEqual(
            questionary_keyboard_input[7], config.gateway.database_migration.release
        )
        self.assertEqual(
            questionary_keyboard_input[8], config.gateway.postgres_db.setup
        )
        self.assertEqual(
            questionary_keyboard_input[9], config.gateway.postgres_db.dbname
        )
        self.assertEqual(
            questionary_keyboard_input[10], config.gateway.postgres_db.user
        )

    def test_setup_docker_compose_with_gateway(self):
        tests_dir = dirname(dirname(__file__))
        fixture_file = join(tests_dir, "fixtures/config-gateway-docker.yaml")
        compose_fixture_file = join(tests_dir, "fixtures/docker-compose.yaml")
        docker_config: DockerConfig = DockerSetup.load_settings(fixture_file)
        self.assertEqual(True, docker_config.gateway.enabled)
        compose_yaml = DockerSetup.render_docker_compose(docker_config)
        with open(compose_fixture_file, "r") as f:
            compose_fixture = yaml.load(f, Loader=UnsafeLoader)
        self.maxDiff = None
        ddiff = DeepDiff(compose_yaml, compose_fixture, ignore_order=True)
        # self.assertEqual({}, ddiff)

    def suite():
        """This defines all the tests of a module"""
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(GatewaySetupTests))
        return suite

    if __name__ == "__main__":
        unittest.TextTestRunner(verbosity=2).run(suite())
