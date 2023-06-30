import os.path
import unittest
from io import StringIO
from unittest import mock

from config.CommonDockerSettings import CommonDockerSettings
from config.Genesis import GenesisConfig
from utils.Network import Network


class NetworkUtilsUnitTests(unittest.TestCase):

    @mock.patch('sys.stdout', new_callable=StringIO, )
    def test_network_id_can_be_validated(self, mock_stdout):
        self.assertEqual(Network.validate_network_id("1"), 1)
        self.assertEqual(Network.validate_network_id("m"), 1)
        self.assertEqual(Network.validate_network_id("M"), 1)
        self.assertEqual(Network.validate_network_id("mainnet"), 1)
        self.assertEqual(Network.validate_network_id("2"), 2)
        self.assertEqual(Network.validate_network_id("s"), 2)
        self.assertEqual(Network.validate_network_id("S"), 2)
        self.assertEqual(Network.validate_network_id("stokenet"), 2)
        self.assertEqual(Network.validate_network_id("STOKENET"), 2)
        self.assertEqual(Network.validate_network_id("10"), 10)
        self.assertEqual(Network.validate_network_id("11"), 11)
        self.assertEqual(Network.validate_network_id("32"), 32)
        self.assertEqual(Network.validate_network_id("33"), 33)
        self.assertEqual(Network.validate_network_id("34"), 34)
        self.assertEqual(Network.validate_network_id("35"), 35)
        # ToDo: Allow all network names to be entered by name
        # self.assertEqual(Network.validate_network_id("enkinet"), 33)
        # self.assertEqual(Network.validate_network_id("Gilganet"), 32)
        # self.assertEqual(Network.validate_network_id("MarduNet"), 36)
        with self.assertRaises(SystemExit) as cm:
            Network.validate_network_id("enkinet")
        self.assertEqual(cm.exception.code, 1)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_input_stuff(self, mock_stdout):
        genesis_location = Network.path_to_genesis_file(1)
        self.assertEqual(genesis_location, None)

        genesis_location = Network.path_to_genesis_file(2)
        self.assertEqual(genesis_location, None)

        with self.assertRaises(SystemExit) as cm:
            with mock.patch('builtins.input', return_value='/tmp/path'):
                genesis_location = Network.path_to_genesis_file(3)
            self.assertEqual(genesis_location, "/tmp/path")
            self.assertEqual(mock_stdout.getvalue(), f" `{genesis_location}` does not exist ")
            self.assertEqual(cm.exception.code, 1)

        with self.assertRaises(SystemExit) as cm:
            with mock.patch('builtins.input', return_value='/tm\\$&(*!@£^(p(^)th'):
                Network.path_to_genesis_file(3)
            self.assertEqual(mock_stdout.getvalue(), "OS error occurred trying to open /tm\\$&(*!@£^(p(^)th")
            self.assertEqual(cm.exception.code, 1)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_default_genesis_files(self, mock_stdout):
        genesis_location = Network.path_to_genesis_file(11)
        self.assertIn("nebunet", genesis_location)
        genesis_location = Network.path_to_genesis_file(12)
        self.assertIn("kisharnet", genesis_location)
        genesis_location = Network.path_to_genesis_file(32)
        self.assertIn("gilganet", genesis_location)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_hammunet_genesis_files(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            settings = CommonDockerSettings({})
            with mock.patch('builtins.input', side_effect=['34', '/tmp/hammunet_genesis.json']):
                settings.ask_network_id(None)
            self.assertIn("hammunet_genesis.json", settings.genesis_json_location)
            self.assertEqual(mock_stdout.getvalue(), f" `{settings.genesis_json_location}` does not exist ")
            self.assertEqual(cm.exception.code, 1)

    def test_create_if_not_exists(self):
        genesisfile_txt = "/tmp/genesisfile.txt"
        # permissions changed on a local test to verify it does not error out when docker has taken ownership
        # self.assertFalse(os.path.exists(genesisfile_txt))
        GenesisConfig.create_genesis_file(genesisfile_txt, "genesis")
        self.assertTrue(os.path.exists(genesisfile_txt))
        GenesisConfig.create_genesis_file(genesisfile_txt, "genesis")
        self.assertTrue(os.path.exists(genesisfile_txt))


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NetworkUtilsUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
