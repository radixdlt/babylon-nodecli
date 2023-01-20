import unittest
import os
import subprocess

from setup import SystemD
from utils.Prompts import Prompts
from utils.PromptFeeder import PromptFeeder
from utils.utils import run_shell_command


class SystemdUnitTests(unittest.TestCase):
    @unittest.skip("Needs enough balance")
    def test_systemd_install_continue_prompt_feed(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_continue.yml"
        PromptFeeder.instance()
        Prompts.confirm_systemd_install("dummy1", "dummy2", "dummy3", "dummy4")

    def test_systemd_install_requires_radixdlt_user(self):
        pass

    def test_systemd_install_generates_keyfile(self):
        pass

    @unittest.skip("Needs enough balance")
    def test_systemd_install_sets_environments_by_creating_file(self):
        SystemD.set_environment_variables("dummypw", "/tmp")
        self.assertTrue(os.path.isfile("/tmp/environment"))

    @unittest.skip("Needs enough balance")
    def test_systemd_creates_default_config(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_default_config.yml"
        PromptFeeder.instance()
        SystemD.setup_default_config("radix:12345dummynode", "1.1.1.1", "/tmp", "???", "false")
        self.assertTrue(os.path.isfile("/tmp/default.config"))
        # ToDo: Test Appending of override lines

    @unittest.skip("Needs enough balance")
    def test_systemd_creates_service_file(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_default_config.yml"
        PromptFeeder.instance()
        SystemD.setup_service_file("someversion", "/tmp", "/tmp/secrets")
        self.assertTrue(os.path.isfile("/etc/systemd/system/radixdlt-node.service"))

    @unittest.skip("can not get it to work")
    def test_systemd_depency_create_service_user_password_optional_input(self):
        # passwd_input= "test\ntest\ntest\n"
        # subprocess.run("cat", input=passwd_input.encode(), shell=False)
        # SystemD.create_service_user_password(oldpassword="mypassword",username="kim.fehrs")

    def test_systemd_downloads_binaries(self):
        pass

    def test_systemd_creates_nginx_config(self):
        pass

    def test_systemd_starts_nginx_service(self):
        pass

    def test_systemd_starts_core_service(self):
        pass


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
