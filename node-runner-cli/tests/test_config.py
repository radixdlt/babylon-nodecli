import os
import unittest

import yaml
from yaml import UnsafeLoader
from pathlib import Path

from config.DockerConfig import DockerConfig
from config.Nginx import SystemdNginxConfig
from config.SystemDConfig import SystemDSettings, extract_network_id_from_arg
from setup.SystemD import SystemD, validate_network_id


class ConfigUnitTests(unittest.TestCase):

    # @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_config_systemd_can_be_instantiated_with_defaults(self):
        config = SystemDSettings({})
        self.assertEqual(config.common_settings.node_dir, "/etc/radixdlt/node")

    def test_config_systemd_nginx_can_be_serialized(self):
        config = SystemdNginxConfig({})
        config.config_url = "randomurl"
        config.release = "1.0.0"
        with open('/tmp/nginxconfig.yaml', 'w') as f:
            yaml.dump(config, f, sort_keys=True, default_flow_style=False)

        if not os.path.isfile(f'/tmp/nginxconfig.yaml'):
            self.fail("Settings File does not exist")
        with open('/tmp/nginxconfig.yaml', 'r') as f:
            new_config = yaml.load(f, Loader=UnsafeLoader)
        self.assertEqual(new_config.config_url, config.config_url)
        self.assertEqual(new_config.release, config.release)

    def test_config_systemd_defaut_config_matches_fixture(self):
        config=SystemDSettings({})
        home_directory = Path.home()
        config.common_settings.node_dir = f"/someDir/node-config"
        config.common_settings.node_secrets_dir = f"/someDir/node-config/secret"
        config_as_yaml = config.to_yaml()
        self.maxDiff = None
        fixture = f"""---
core_node_settings:
  nodetype: fullnode
  keydetails:
    keyfile_path: {home_directory}/node-config
    keyfile_name: node-keystore.ks
  repo: radixdlt/radixdlt-core
  data_directory: {home_directory}/data
  enable_transaction: 'false'
  java_opts: --enable-preview -server -Xms8g -Xmx8g  -XX:MaxDirectMemorySize=2048m
    -XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts
    -Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom -DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector
common_settings:
  nginx_settings:
    dir: /etc/nginx
    secrets_dir: /etc/nginx/secrets
  service_user: radixdlt
  node_dir: /someDir/node-config
  node_secrets_dir: /someDir/node-config/secret
  network_id: 1
"""
        self.assertEqual(config_as_yaml, fixture)

    def test_config_docker_defaut_config_matches_fixture(self):
        config = DockerConfig({})
        config_as_yaml = config.to_yaml()
        home_directory = Path.home()
        self.maxDiff = None
        fixture = f"""---
core_node_settings:
  nodetype: fullnode
  keydetails:
    keyfile_path: {home_directory}/node-config
    keyfile_name: node-keystore.ks
  repo: radixdlt/radixdlt-core
  data_directory: {home_directory}/data
  enable_transaction: 'false'
  java_opts: --enable-preview -server -Xms8g -Xmx8g  -XX:MaxDirectMemorySize=2048m
    -XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts
    -Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom -DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector
common_settings:
  nginx_settings:
    protect_gateway: 'true'
    gateway_behind_auth: 'true'
    enable_transaction_api: 'false'
    protect_core: 'true'
    repo: radixdlt/radixdlt-nginx
  docker_compose: {home_directory}/docker-compose.yml
gateway_settings:
  data_aggregator:
    repo: radixdlt/ng-data-aggregator
    restart: unless-stopped
    coreApiNode:
      Name: Core
      core_api_address: http://core:3333
      trust_weighting: 1
      request_weighting: 1
      enabled: 'true'
  gateway_api:
    repo: radixdlt/ng-gateway-api
    coreApiNode:
      Name: Core
      core_api_address: http://core:3333
      trust_weighting: 1
      request_weighting: 1
      enabled: 'true'
    restart: unless-stopped
    enable_swagger: 'true'
    max_page_size: '30'
  postgres_db:
    user: postgres
    dbname: radixdlt_ledger
    setup: local
    host: host.docker.internal:5432
"""
        self.assertEqual(config_as_yaml, fixture)

    def test_network_id_can_be_parsed(self):
        self.assertEqual(validate_network_id("1"), 1)
        self.assertEqual(validate_network_id("m"), 1)
        self.assertEqual(validate_network_id("M"), 1)
        self.assertEqual(validate_network_id("mainnet"), 1)
        self.assertEqual(validate_network_id("2"), 2)
        self.assertEqual(validate_network_id("s"), 2)
        self.assertEqual(validate_network_id("S"), 2)
        self.assertEqual(validate_network_id("stokenet"), 2)

def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
