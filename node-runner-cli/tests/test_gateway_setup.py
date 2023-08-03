import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import urllib3

from config.SystemDConfig import SystemDConfig
from setup.GatewaySetup import GatewaySetup
from utils.Prompts import Prompts


class GatewaySetupTests(unittest.TestCase):
    fixture: SystemDConfig = SystemDConfig({})

    @classmethod
    def setUpClass(cls):
        cls.fixture.gateway.enabled = True
        cls.fixture.gateway.gateway_api.coreApiNode.core_api_address = "https://test:1234"
        cls.fixture.gateway.gateway_api.coreApiNode.Name = "Dummy"
        cls.fixture.gateway.gateway_api.coreApiNode.enabled = "True"
        cls.fixture.gateway.gateway_api.coreApiNode.basic_auth_user = "coreapiuser"
        cls.fixture.gateway.gateway_api.coreApiNode.basic_auth_password = "coreapipassword"
        cls.fixture.gateway.gateway_api.coreApiNode.disable_core_api_https_certificate_checks = "false"

        cls.fixture.gateway.gateway_api.release = "testrelease"
        cls.fixture.gateway.gateway_api.repo = "radixdlt/gateway-test-dummy"

        cls.fixture.gateway.data_aggregator.coreApiNode = cls.fixture.gateway.gateway_api.coreApiNode
        cls.fixture.gateway.data_aggregator.release = "testrelease"
        cls.fixture.gateway.data_aggregator.repo = "radixdlt/gateway-test-dummy"
        cls.fixture.gateway.data_aggregator.NetworkName = "randomnet"

        cls.fixture.gateway.database_migration.release = "testrelease"
        cls.fixture.gateway.database_migration.repo = "radixdlt/gateway-test-dummy"

        cls.fixture.gateway.postgres_db.setup = "local"
        cls.fixture.gateway.postgres_db.user = "testpostgresuser"
        cls.fixture.gateway.postgres_db.password = "testpostgrespassword"
        cls.fixture.gateway.postgres_db.host = "localhost:5678"
        cls.fixture.gateway.postgres_db.dbname = "databasename"
        cls.fixture.gateway.docker_compose_file = "/tmp/gateway.docker-compose.yml"

    @patch('sys.stdout', new_callable=StringIO)
    def test_setup_gateway_generate_compose_file(self, mockout):
        urllib3.disable_warnings()
        with patch('builtins.input', side_effect=['n']):
            GatewaySetup.install_standalone_gateway(self.fixture)
            docker_compose_string = self.read_compose_file_from_disc()
            self.assertEqual(self.render_compose_fixture(), docker_compose_string.strip())

    def read_compose_file_from_disc(self):
        docker_compose_file_path = self.fixture.gateway.docker_compose_file
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
      GatewayApi__Network__CoreApiNodes__0__CoreApiAuthorizationHeader: ""
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
      DataAggregator__Network__CoreApiNodes__0__CoreApiAuthorizationHeader: ""
      DataAggregator__Network__CoreApiNodes__0__TrustWeighting:  "1"
      DataAggregator__Network__CoreApiNodes__0__Enabled:  "{self.fixture.gateway.gateway_api.coreApiNode.enabled}"
  database_migrations: # This is the base -- the _image and _built containers are defined below
    image: {self.fixture.gateway.database_migration.repo}:{self.fixture.gateway.database_migration.release}
    environment:
      ConnectionStrings__NetworkGatewayMigrations: Host={self.fixture.gateway.postgres_db.host};Database={self.fixture.gateway.postgres_db.dbname};Username={self.fixture.gateway.postgres_db.user};Password={self.fixture.gateway.postgres_db.password}
    extra_hosts:
    - "host.docker.internal:host-gateway" """.strip()

    @patch('sys.stdout', new_callable=StringIO)
    def test_setup_gateway(self, mockout):
        urllib3.disable_warnings()
        with patch('builtins.input', side_effect=['', '', '', 'postgres', 'radix', '', '', '']):
            gateway_config = GatewaySetup.ask_gateway_standalone_docker("radix")
            self.assertEqual(True, gateway_config.enabled)
            self.assertEqual("http://localhost:3332", gateway_config.gateway_api.coreApiNode.core_api_address)
            self.assertEqual("postgres", gateway_config.postgres_db.user)
            self.assertEqual("radix", gateway_config.postgres_db.password)

    @patch('sys.stdout', new_callable=StringIO)
    def test_setup_gateway_ask_core_api(self, mockout):
        urllib3.disable_warnings()
        keyboard_input = ["", "CoreNodeName"]
        default_value = "http://localhost:3332"
        with patch('builtins.input', side_effect=keyboard_input):
            core_api = GatewaySetup.ask_core_api_node_settings(default_value)

        self.assertEqual(default_value, core_api.core_api_address)
        self.assertEqual("CoreNodeName", core_api.Name)

    @patch('sys.stdout', new_callable=StringIO)
    def test_setup_gateway_get_CoreApiAddress(self, mockout):
        urllib3.disable_warnings()
        # Takes default value
        keyboard_input = ""
        default_value = "http://localhost:3332"
        with patch('builtins.input', side_effect=[keyboard_input]):
            # Core Node Address
            core_api_address = Prompts.get_CoreApiAddress(default_value)

        self.assertEqual(default_value, core_api_address)
        # Overrides with input
        keyboard_input = "http://core:3333"
        with patch('builtins.input', side_effect=[keyboard_input]):
            # Core Node Address
            core_api_address = Prompts.get_CoreApiAddress(default_value)
        self.assertEqual(keyboard_input, core_api_address)


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GatewaySetupTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
