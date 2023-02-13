import unittest

from unittest import mock
from io import StringIO

from config.DockerConfig import CoreDockerSettings
from utils.Network import Network


class ValidatorUnitTests(unittest.TestCase):

    def test_can_set_validator_address(self):
        core_settings = CoreDockerSettings({})
        core_settings.set_validator_address("validator_mock")
        self.assertEqual(core_settings.validator_address, "validator_mock")


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ValidatorUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
