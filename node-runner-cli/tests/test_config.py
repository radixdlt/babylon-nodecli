import os
import unittest
from pathlib import Path

import yaml
from yaml import UnsafeLoader

from config.DockerConfig import DockerConfig
from config.Nginx import SystemdNginxConfig, DockerNginxConfig
from config.SystemDConfig import SystemDSettings
from utils.Network import Network


class ConfigUnitTests(unittest.TestCase):

    # @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_config_systemd_can_be_instantiated_with_defaults(self):
        config = SystemDSettings({})
        self.assertEqual(config.core_node.node_dir, "/etc/radixdlt/node")

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
        config = SystemDSettings({})
        config.migration.use_olympia = True
        home_directory = Path.home()
        config.core_node.node_dir = f"/someDir/babylon-node-config"
        config.core_node.node_secrets_dir = f"/someDir/babylon-node-config/secret"
        config_as_yaml = config.to_yaml()
        self.maxDiff = None
        fixture = f"""---
common_config:
  network_id: 1
  nginx_settings:
    dir: /etc/nginx
    enable_transaction_api: 'false'
    mode: systemd
    protect_core: 'true'
    secrets_dir: /etc/nginx/secrets
  service_user: radixdlt
core_node:
  data_directory: {home_directory}/babylon-ledger
  enable_transaction: 'false'
  java_opts: --enable-preview -server -Xms8g -Xmx8g  -XX:MaxDirectMemorySize=2048m
    -XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts
    -Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom -DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector
  keydetails:
    keyfile_name: node-keystore.ks
    keyfile_path: {home_directory}/babylon-node-config
    keygen_tag: v1.4.1
  node_dir: /someDir/babylon-node-config
  node_secrets_dir: /someDir/babylon-node-config/secret
  nodetype: fullnode
gateway:
  data_aggregator:
    coreApiNode:
      Name: Core
      core_api_address: http://core:3333
      enabled: 'true'
      request_weighting: 1
      trust_weighting: 1
    repo: radixdlt/babylon-ng-data-aggregator
    restart: unless-stopped
  database_migration:
    repo: radixdlt/babylon-ng-database-migrations
  docker_compose_file: ~/gateway.docker-compose.yml
  gateway_api:
    coreApiNode:
      Name: Core
      core_api_address: http://core:3333
      enabled: 'true'
      request_weighting: 1
      trust_weighting: 1
    enable_swagger: 'true'
    max_page_size: '30'
    repo: radixdlt/babylon-ng-gateway-api
    restart: unless-stopped
  postgres_db:
    dbname: radixdlt_ledger
    host: host.docker.internal:5432
    setup: local
    user: postgres
migration:
  use_olympia: true
"""
        self.assertEqual(fixture, config_as_yaml)

    def test_config_docker_defaut_config_matches_fixture(self):
        config = DockerConfig({})
        config.migration.use_olympia = True
        config_as_yaml = config.to_yaml()
        home_directory = Path.home()
        self.maxDiff = None
        fixture = f"""---
core_node:
  nodetype: fullnode
  keydetails:
    keyfile_path: {home_directory}/babylon-node-config
    keyfile_name: node-keystore.ks
    keygen_tag: v1.4.1
  repo: radixdlt/babylon-node
  data_directory: {home_directory}/babylon-ledger
  enable_transaction: 'false'
  java_opts: --enable-preview -server -Xms8g -Xmx8g  -XX:MaxDirectMemorySize=2048m
    -XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts
    -Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom -DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector
common_config:
  nginx_settings:
    mode: docker
    protect_gateway: 'true'
    gateway_behind_auth: 'true'
    enable_transaction_api: 'false'
    protect_core: 'true'
    repo: radixdlt/babylon-nginx
  docker_compose: {home_directory}/docker-compose.yml
gateway:
  data_aggregator:
    repo: radixdlt/babylon-ng-data-aggregator
    restart: unless-stopped
    coreApiNode:
      Name: Core
      core_api_address: http://core:3333
      trust_weighting: 1
      request_weighting: 1
      enabled: 'true'
  gateway_api:
    repo: radixdlt/babylon-ng-gateway-api
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
  database_migration:
    repo: radixdlt/babylon-ng-database-migrations
  docker_compose_file: ~/gateway.docker-compose.yml
migration:
  use_olympia: true
"""
        self.assertEqual(fixture, config_as_yaml)

    def test_network_id_can_be_parsed(self):
        self.assertEqual(Network.validate_network_id("1"), 1)
        self.assertEqual(Network.validate_network_id("m"), 1)
        self.assertEqual(Network.validate_network_id("M"), 1)
        self.assertEqual(Network.validate_network_id("mainnet"), 1)
        self.assertEqual(Network.validate_network_id("2"), 2)
        self.assertEqual(Network.validate_network_id("s"), 2)
        self.assertEqual(Network.validate_network_id("S"), 2)
        self.assertEqual(Network.validate_network_id("stokenet"), 2)


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConfigUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
