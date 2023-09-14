# import unittest
#
# from config.KeyDetails import KeyDetails
# from config.SystemDConfig import SystemDConfig
# from utils.utils import Helpers
#
#
# class DiffUnitTests(unittest.TestCase):
#
#     def test_human_readable_diff_with_keydetails(self):
#         first = KeyDetails({})
#         second = KeyDetails({})
#         first.keyfile_name = "hans.ks"
#         second.keystore_password = "secret"
#         print(
#             Helpers.compare_human_readable(first.to_dict(), second.to_dict())
#         )
#         self.assertEqual(('  {\n'
#                           '\x1b[31m-     "keyfile_name": "hans.ks",\x1b\x1b[0m\n'
#                           '\x1b[32m+     "keyfile_name": "node-keystore.ks",\x1b\x1b[0m\n'
#                           '      "keyfile_path": "/Users/kim.fehrs/babylon-node-config",\n'
#                           '      "keygen_tag": "v1.4.1",\n'
#                           '\x1b[31m-     "keystore_password": ""\x1b\x1b[0m\n'
#                           '\x1b[32m+     "keystore_password": "secret"\x1b\x1b[0m\n'
#                           '  }\n'), Helpers.compare_human_readable(first.to_dict(), second.to_dict()))
#
#     def test_human_readable_diff_with_systemd_config(self):
#         first = SystemDConfig({})
#         second = SystemDConfig({})
#         first.gateway.enabled = True
#         second.common_config.nginx_settings.release = "other"
#         print(
#             Helpers.compare_human_readable(first.to_dict(), second.to_dict())
#         )
#         self.assertEqual(('  {\n'
#                           '      "common_config": {\n'
#                           '          "genesis_bin_data_file": "",\n'
#                           '          "host_ip": "",\n'
#                           '          "network_id": 1,\n'
#                           '          "network_name": "",\n'
#                           '          "nginx_settings": {\n'
#                           '              "config_url": "",\n'
#                           '              "dir": "/etc/nginx",\n'
#                           '              "enable_transaction_api": "false",\n'
#                           '              "mode": "systemd",\n'
#                           '              "protect_core": "true",\n'
#                           '\x1b[31m-             "release": "",\x1b\x1b[0m\n'
#                           '\x1b[32m+             "release": "other",\x1b\x1b[0m\n'
#                           '              "secrets_dir": "/etc/nginx/secrets"\n'
#                           '          },\n'
#                           '          "service_user": "radixdlt"\n'
#                           '      },\n'
#                           '      "core_node": {\n'
#                           '          "core_binary_url": "",\n'
#                           '          "core_library_url": "",\n'
#                           '          "core_release": "",\n'
#                           '          "data_directory": "/Users/kim.fehrs/babylon-ledger",\n'
#                           '          "enable_transaction": "false",\n'
#                           '          "java_opts": "--enable-preview -server -Xms16g -Xmx16g  '
#                           '-XX:MaxDirectMemorySize=2048m -XX:+HeapDumpOnOutOfMemoryError '
#                           '-XX:+UseCompressedOops '
#                           '-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts '
#                           '-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom '
#                           '-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector",\n'
#                           '          "keydetails": {\n'
#                           '              "keyfile_name": "node-keystore.ks",\n'
#                           '              "keyfile_path": "/Users/kim.fehrs/babylon-node-config",\n'
#                           '              "keygen_tag": "v1.4.1",\n'
#                           '              "keystore_password": ""\n'
#                           '          },\n'
#                           '          "node_dir": "/etc/radixdlt/node",\n'
#                           '          "node_secrets_dir": "/etc/radixdlt/node/secrets",\n'
#                           '          "nodetype": "fullnode",\n'
#                           '          "trusted_node": "",\n'
#                           '          "validator_address": ""\n'
#                           '      },\n'
#                           '      "gateway": {\n'
#                           '          "data_aggregator": {\n'
#                           '              "coreApiNode": {\n'
#                           '                  "Name": "Core",\n'
#                           '                  "auth_header": "",\n'
#                           '                  "basic_auth_password": "",\n'
#                           '                  "basic_auth_user": "",\n'
#                           '                  "core_api_address": "http://core:3333/core",\n'
#                           '                  "disable_core_api_https_certificate_checks": "false",\n'
#                           '                  "enabled": "true",\n'
#                           '                  "request_weighting": 1,\n'
#                           '                  "trust_weighting": 1\n'
#                           '              },\n'
#                           '              "release": "",\n'
#                           '              "repo": "radixdlt/babylon-ng-data-aggregator",\n'
#                           '              "restart": "unless-stopped"\n'
#                           '          },\n'
#                           '          "database_migration": {\n'
#                           '              "release": "",\n'
#                           '              "repo": "radixdlt/babylon-ng-database-migrations"\n'
#                           '          },\n'
#                           '          "docker_compose": "/Users/kim.fehrs/gateway.docker-compose.yml",\n'
#                           '\x1b[31m-         "enabled": true,\x1b\x1b[0m\n'
#                           '\x1b[32m+         "enabled": false,\x1b\x1b[0m\n'
#                           '          "gateway_api": {\n'
#                           '              "coreApiNode": {\n'
#                           '                  "Name": "Core",\n'
#                           '                  "auth_header": "",\n'
#                           '                  "basic_auth_password": "",\n'
#                           '                  "basic_auth_user": "",\n'
#                           '                  "core_api_address": "http://core:3333/core",\n'
#                           '                  "disable_core_api_https_certificate_checks": "false",\n'
#                           '                  "enabled": "true",\n'
#                           '                  "request_weighting": 1,\n'
#                           '                  "trust_weighting": 1\n'
#                           '              },\n'
#                           '              "enable_swagger": "true",\n'
#                           '              "max_page_size": "30",\n'
#                           '              "release": "",\n'
#                           '              "repo": "radixdlt/babylon-ng-gateway-api",\n'
#                           '              "restart": "unless-stopped"\n'
#                           '          },\n'
#                           '          "postgres_db": {\n'
#                           '              "dbname": "radixdlt_ledger",\n'
#                           '              "host": "host.docker.internal:5432",\n'
#                           '              "password": "",\n'
#                           '              "setup": "local",\n'
#                           '              "user": "postgres"\n'
#                           '          }\n'
#                           '      },\n'
#                           '      "migration": {\n'
#                           '          "olympia_node_auth_password": "",\n'
#                           '          "olympia_node_auth_user": "admin",\n'
#                           '          "olympia_node_bech32_address": "",\n'
#                           '          "olympia_node_url": "http://localhost:3332",\n'
#                           '          "use_olympia": false\n'
#                           '      }\n'
#                           '  }\n'), Helpers.compare_human_readable(first.to_dict(), second.to_dict()))
