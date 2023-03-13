import unittest

from unittest import mock
from io import StringIO

import urllib3

import github.github
from utils.Network import Network


class LatestReleaseUnitTests(unittest.TestCase):

    def test_latest_releases(self):
        urllib3.disable_warnings()
        self.assertEqual(github.github.latest_release("radixdlt/babylon-node"), "betanet-v2-2e0f369d5")
        self.assertEqual(github.github.latest_release("radixdlt/babylon-nginx"), "1.0.0-rc2")
        self.assertEqual(github.github.latest_release("radixdlt/babylon-gateway"), "betanet-v2-87f7371c5")


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LatestReleaseUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
