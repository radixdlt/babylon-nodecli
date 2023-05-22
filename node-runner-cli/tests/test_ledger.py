import unittest

from unittest.mock import patch
from radixnode import main
class LedgerUnitTests(unittest.TestCase):

    def test_ledger_config_can_run_without_prompt(self):
        with patch("sys.argv",
                   ["main", "ledger", "sync",
                    "-d", "./",
                    "--bucketname", "olympia-mainnet-ledger-backups",
                    "--bucketfolder", "mainnet/mainnet_eu_west_1_fullnode2"]):
            main()

    def suite():
        """ This defines all the tests of a module"""
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(LedgerUnitTests))
        return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
