import unittest
import os
from utils.Prompts import Prompts
from utils.PromptFeeder import PromptFeeder


class SystemdUnitTests(unittest.TestCase):

    def test_systemd_install_continue_prompt_feed(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_continue.yml"
        PromptFeeder.instance()
        Prompts.ask_continue_systemd_install("dummy1", "dummy2", "dummy3", "dummy4")


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
