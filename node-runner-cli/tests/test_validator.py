import os
import unittest
from io import StringIO
from unittest import mock

import yaml

from config.DockerConfig import CoreDockerSettings, DockerConfig
from config.Renderer import Renderer
from utils.PromptFeeder import PromptFeeder
from utils.Prompts import Prompts


class ValidatorUnitTests(unittest.TestCase):

    def test_can_set_validator_address(self):
        core_settings = CoreDockerSettings({})
        core_settings.set_validator_address("validator_mock")
        self.assertEqual(core_settings.validator_address, "validator_mock")

    def test_prompt_validator_address(self):
        with mock.patch('builtins.input', side_effect=['Y', 'validator_address_5']):
            validator_address = Prompts.ask_validator_address()
            self.assertEqual(validator_address, "validator_address_5")
        with mock.patch('builtins.input', side_effect=['n']):
            validator_address = Prompts.ask_validator_address()
            self.assertEqual(validator_address, "")

    def test_validator_address_get_templated_into_docker_compose(self):
        validator_address_fixture = "validator_mock"
        settings = {'core_node': {'validator_address': validator_address_fixture,
                                  'repo': 'some',
                                  'core_release': '2.4',
                                  'keydetails': {'something': 'else'}
                                  },
                    'common_config': {'test': 'test'}}
        compose_yml = Renderer().load_file_based_template("radix-fullnode-compose.yml.j2").render(
            dict(settings)).to_yaml()
        compose_yml_str = str(compose_yml)
        self.assertTrue(validator_address_fixture in compose_yml_str)

    def test_validator_address_gets_omitted_in_docker_compose_if_not_set(self):
        settings = {'core_node': {'repo': 'some',
                                  'core_release': '2.4',
                                  'keydetails': {'something': 'else'}
                                  },
                    'common_config': {'test': 'test'}}
        compose_yml = Renderer().load_file_based_template("radix-fullnode-compose.yml.j2").render(
            dict(settings)).to_yaml()
        compose_yml_str = str(compose_yml)
        self.assertFalse("RADIXDLT_CONSENSUS_VALIDATOR_ADDRESS" in compose_yml_str)

    def test_validator_address_included_in_dict_from_object(self):
        config = DockerConfig("1.0.0")
        config.core_node_settings = CoreDockerSettings({})
        config.core_node_settings.validator_address = "validator_mock"
        # ToDo: This is too looesely coupled. Implement DockerConfig save and load from/to Object and remove this test
        yaml_config = yaml.dump(config, default_flow_style=False, explicit_start=True, allow_unicode=True)
        self.assertTrue("validator_address" in str(yaml_config))
        self.assertTrue("validator_mock" in str(yaml_config))

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_validator_promptfeed(self, mock_out):
        os.environ['PROMPT_FEEDS'] = "test-prompts/individual-prompts/validator_address.yml"
        PromptFeeder.prompts_feed = PromptFeeder.instance().load_prompt_feeds()
        address = Prompts.ask_validator_address()
        self.assertEqual("validator_mock", address)



def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ValidatorUnitTests))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
