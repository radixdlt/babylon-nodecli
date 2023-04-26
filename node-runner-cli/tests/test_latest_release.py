import unittest

import urllib3

import github.github


class LatestReleaseUnitTests(unittest.TestCase):

    def test_latest_releases(self):
        urllib3.disable_warnings()
        # self.assertEqual(github.github.latest_release("radixdlt/babylon-node"), "rcnet-v1.1-682b897")
        # self.assertEqual(github.github.latest_release("radixdlt/babylon-nginx"), "1.0.0-rc2")
        # self.assertEqual(github.github.latest_release("radixdlt/babylon-gateway"), "rcnet-v1-a8da752")


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LatestReleaseUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
