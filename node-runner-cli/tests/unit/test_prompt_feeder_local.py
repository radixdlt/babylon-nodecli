import unittest
from io import StringIO
from unittest.mock import patch

import urllib3

from babylonnode import main
from config.DockerConfig import DockerConfig
from setup.DockerSetup import DockerSetup


class PromptFeederUnitTests(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_docker_config_gateway_external_postgres(self, mockout):
        urllib3.disable_warnings()
        PROMPT_NETWORKID = "14"
        PROMPT_FULLNODE_YES_NO = "Y"
        # PROMPT_SEEDNODES = ''
        PROMPT_VALIDATOR_ADDRESS = "n"
        PROMPT_EXISTING_KEYSTORE = "Y"
        PROMPT_KEYSTORE_LOCATION = ""
        PROMPT_KEYSTORE_FILE_NAME = ""
        PROMPT_LEDGER_LOCATION = ""
        PROMPT_LEDGER_SNAPSHOT = ""
        PROMPT_NGINX_PROTECT_CORE_API = ""
        PROMPT_ENABLE_GATEWAY = "Y"
        PROMPT_GATEWAY_CORE_API_URL = "http://core:3333/core"
        PROMPT_GATEWAY_CORE_API_NAME = ""
        PROMPT_POSTGRES_LOCAL_REMOTE = "remote"
        PROMPT_POSTGRES_REMOTE_URL = "postgres"
        PROMPT_POSTGRES_REMOTE_PORT = "5432"
        PROMPT_POSTGRES_DATABASE_NAME = ""
        PROMPT_POSTGRES_USERNAME = ""
        PROMPT_POSTGRES_PASSWORD = "radix"
        PROMPT_GATEWAY_IMAGE_VERSION = ""
        PROMPT_MIGRATION_IMAGE_VERSION = ""
        PROMPT_AGGREGATOR_IMAGE_VERSION = ""
        PROMPT_NGINX_PROTECT_GATEWAY = "true"
        PROMPT_NGINX_IMAGE_VERSION = ""
        PROMPT_CONFIRM_CONFIG = "Y"
        with patch(
            "builtins.input",
            side_effect=[
                PROMPT_NETWORKID,
                PROMPT_FULLNODE_YES_NO,
                # PROMPT_SEEDNODES,
                PROMPT_VALIDATOR_ADDRESS,
                PROMPT_EXISTING_KEYSTORE,
                PROMPT_KEYSTORE_LOCATION,
                PROMPT_KEYSTORE_FILE_NAME,
                PROMPT_LEDGER_LOCATION,
                PROMPT_LEDGER_SNAPSHOT,
                PROMPT_NGINX_PROTECT_CORE_API,
                PROMPT_ENABLE_GATEWAY,
                PROMPT_GATEWAY_CORE_API_URL,
                PROMPT_GATEWAY_CORE_API_NAME,
                PROMPT_POSTGRES_LOCAL_REMOTE,
                PROMPT_POSTGRES_REMOTE_URL,
                PROMPT_POSTGRES_REMOTE_PORT,
                PROMPT_POSTGRES_DATABASE_NAME,
                PROMPT_POSTGRES_USERNAME,
                PROMPT_POSTGRES_PASSWORD,
                PROMPT_GATEWAY_IMAGE_VERSION,
                PROMPT_MIGRATION_IMAGE_VERSION,
                PROMPT_AGGREGATOR_IMAGE_VERSION,
                PROMPT_NGINX_PROTECT_GATEWAY,
                PROMPT_NGINX_IMAGE_VERSION,
                PROMPT_CONFIRM_CONFIG,
            ],
        ):
            with patch(
                "sys.argv",
                [
                    "main",
                    "docker",
                    "config",
                    "-m",
                    "DETAILED",
                    "-k",
                    "radix",
                    "-nk",
                    "-t",
                    "asdasd",
                ],
            ):
                main()

    @patch("sys.stdout", new_callable=StringIO)
    def test_docker_config_all_local(self, mockout):
        urllib3.disable_warnings()
        with open("/tmp/genesis.json", "w") as fp:
            pass

        PROMPT_NETWORKID = "2"
        PROMPT_FULLNODE_YES_NO = "Y"
        PROMPT_SEEDNODES = "radix://node_tdx_22_1qvsml9pe32rzcrmw6jx204gjeng09adzkqqfz0ewhxwmjsaas99jzrje4u3@34.243.93.185"
        PROMPT_VALIDATOR_ADDRESS = "N"
        PROMPT_EXISTING_KEYSTORE = "Y"
        PROMPT_KEYSTORE_LOCATION = "/tmp/babylon-node-config"
        PROMPT_KEYSTORE_FILE_NAME = "node-keystore.ks"
        PROMPT_LEDGER_LOCATION = "/tmp/data"
        PROMPT_LEDGER_SNAPSHOT = "true"
        PROMPT_NGINX_PROTECT_CORE_API = "true"
        PROMPT_ENABLE_GATEWAY = "Y"
        PROMPT_GATEWAY_CORE_API_URL = "http://core:3333/core"
        PROMPT_GATEWAY_CORE_API_NAME = "core"
        PROMPT_POSTGRES_LOCAL_REMOTE = "local"
        PROMPT_POSTGRES_USERNAME = "postgres"
        PROMPT_POSTGRES_DATABASE_NAME = "radix-ledger"
        PROMPT_POSTGRES_PASSWORD = "pgpassword"
        PROMPT_GATEWAY_IMAGE_VERSION = ""
        PROMPT_MIGRATION_IMAGE_VERSION = ""
        PROMPT_AGGREGATOR_IMAGE_VERSION = ""
        PROMPT_NGINX_PROTECT_GATEWAY = "true"
        PROMPT_NGINX_IMAGE_VERSION = ""
        PROMPT_CONFIRM_CONFIG = "Y"
        with patch(
            "builtins.input",
            side_effect=[
                PROMPT_NETWORKID,
                PROMPT_FULLNODE_YES_NO,
                PROMPT_SEEDNODES,
                PROMPT_VALIDATOR_ADDRESS,
                PROMPT_EXISTING_KEYSTORE,
                PROMPT_KEYSTORE_LOCATION,
                PROMPT_KEYSTORE_FILE_NAME,
                PROMPT_LEDGER_LOCATION,
                PROMPT_LEDGER_SNAPSHOT,
                PROMPT_NGINX_PROTECT_CORE_API,
                PROMPT_ENABLE_GATEWAY,
                PROMPT_GATEWAY_CORE_API_URL,
                PROMPT_GATEWAY_CORE_API_NAME,
                PROMPT_POSTGRES_LOCAL_REMOTE,
                PROMPT_POSTGRES_USERNAME,
                PROMPT_POSTGRES_DATABASE_NAME,
                PROMPT_POSTGRES_PASSWORD,
                PROMPT_GATEWAY_IMAGE_VERSION,
                PROMPT_MIGRATION_IMAGE_VERSION,
                PROMPT_AGGREGATOR_IMAGE_VERSION,
                PROMPT_NGINX_PROTECT_GATEWAY,
                PROMPT_NGINX_IMAGE_VERSION,
            ],
        ):
            with patch(
                "sys.argv",
                [
                    "main",
                    "docker",
                    "config",
                    "-m",
                    "DETAILED",
                    "-k",
                    "radix",
                    "-nk",
                    "-a",
                    "-d",
                    "/tmp",
                ],
            ):
                main()

            docker_config: DockerConfig = DockerSetup.load_settings("/tmp/config.yaml")
            self.assertEqual(
                "radix", docker_config.core_node.keydetails.keystore_password
            )


def suite():
    """This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PromptFeederUnitTests))
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
