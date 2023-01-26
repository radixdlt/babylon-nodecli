import os
import unittest
from unittest.mock import patch

from config.KeyDetails import KeyDetails
from config.SystemDConfig import SystemDSettings
from radixnode import main
from setup import SystemD
from utils.PromptFeeder import PromptFeeder
from utils.utils import Helpers


class SystemdUnitTests(unittest.TestCase):

    @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_systemd_install_continue_prompt_feed(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_continue.yml"
        PromptFeeder.instance().load_prompt_feeds()
        SystemD.confirm_config("dummy1", "dummy2", "dummy3", "dummy4")

    def test_systemd_install_requires_radixdlt_user(self):
        pass

    def test_systemd_install_generates_keyfile(self):
        pass

    def test_systemd_install_sets_environments_by_creating_file(self):
        SystemD.set_environment_variables("dummypw", "/tmp")
        self.assertTrue(os.path.isfile("/tmp/environment"))


    def test_systemd_creates_default_config_without_asking(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_default_config.yml"
        PromptFeeder.instance().load_prompt_feeds()
        SystemD.setup_default_config("radix:12345dummynode", "1.1.1.1", "/tmp", "???", "false")
        self.assertTrue(os.path.isfile("/tmp/default.config"))
        # ToDo: Test Appending of override lines

    @unittest.skip("Tests with PROMPT_FEEDS can only be run individually")
    def test_systemd_creates_service_file_without_asking(self):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/systemd_install_default_config.yml"
        PromptFeeder.instance().load_prompt_feeds()
        PromptFeeder.instance()
        SystemD.setup_service_file("someversion", "/tmp", "/tmp/secrets", "/tmp/servicefile")
        self.assertTrue(os.path.isfile("/tmp/servicefile"))


    def test_systemd_config_can_run_without_prompt(self):
        with patch("sys.argv",
                   ["main", "systemd", "config",
                    "-a",
                    "-t", "somenode",
                    "-i", "123.123.123.123",
                    "-kp", "password",
                    "-n", "S",
                    "-d", "/tmp/config",
                    "-dd", "/tmp/data"]):
            main()

    def test_systemd_config_can_be_saved_and_restored_as_yaml(self):
        # Make Python Class YAML Serializable
        settings = SystemDSettings({})
        key_details = KeyDetails({})
        settings.core_node_settings.keydetails = key_details
        settings.host_ip = "6.6.6.6"

        config_file = f"{Helpers.get_default_node_config_dir()}/config.yaml"
        SystemD.save_settings(settings, config_file)

        new_settings = SystemD.load_settings(config_file)
        self.assertEqual(settings.host_ip, new_settings.host_ip)

    @unittest.skip("Can only be executed on Ubuntu")
    def test_systemd_dependencies(self):
        with patch("sys.argv",
                   ["main", "systemd", "dependencies"]):
            main()


def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SystemdUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
