import os
import unittest
from unittest.mock import patch

import yaml
from yaml import UnsafeLoader

from config.SystemDConfig import SystemDSettings
from config.Nginx import SystemdNginxConfig
from config.KeyDetails import KeyDetails
from radixnode import main
from setup import SystemD
from utils.PromptFeeder import PromptFeeder


class ConfigUnitTests(unittest.TestCase):

    # @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_config_systemd_can_be_instantiated_with_defaults(self):
        config = SystemDSettings()
        self.assertEqual(config.node_dir, "/etc/radixdlt/node")

    def test_config_systemd_nginx_can_be_serialized(self):
        config = SystemdNginxConfig()
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



def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
