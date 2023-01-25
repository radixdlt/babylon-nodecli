import os
import unittest
from unittest.mock import patch

from config.SystemDConfig import SystemDSettings
from config.KeyDetails import KeyDetails
from radixnode import main
from setup import SystemD
from utils.PromptFeeder import PromptFeeder


class ConfigUnitTests(unittest.TestCase):

    # @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_config_systemd_can_be_instantiated_with_defaults(self):
        config = SystemDSettings()
        self.assertEqual(config.node_dir, "/etc/radixdlt/node")


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
