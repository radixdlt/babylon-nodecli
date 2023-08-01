import unittest
from io import StringIO
from unittest.mock import patch

import urllib3

from setup.GatewaySetup import GatewaySetup
from utils.Prompts import Prompts


class GatewaySetupTests(unittest.TestCase):

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
