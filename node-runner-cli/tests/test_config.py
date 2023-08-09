import os
import unittest

import yaml
from yaml import UnsafeLoader

from config.Nginx import SystemdNginxConfig
from config.SystemDConfig import SystemDConfig
from utils.Network import Network


class ConfigUnitTests(unittest.TestCase):

    # @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_config_systemd_can_be_instantiated_with_defaults(self):
        config = SystemDConfig({})
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
