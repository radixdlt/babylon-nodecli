from core_client import Configuration, ApiException
from core_client.api import network_api
from core_client.model.data import Data
from core_client.model.network_configuration_response import NetworkConfigurationResponse
from core_client.model.network_status_request import NetworkStatusRequest
from core_client.model.operation import Operation
from core_client.model.operation_group import OperationGroup
from core_client.model.prepared_validator_registered import PreparedValidatorRegistered
from core_client.model.validator_metadata import ValidatorMetadata
import core_client as core_api
from api.Api import API
from utils.utils import Helpers


class CoreApiHelper(API):
    system_config: Configuration = None
    network_identifier = None

    def __init__(self, verify_ssl):
        node_host = API.get_host_info()
        self.system_config = core_api.Configuration(node_host, verify_ssl=verify_ssl)

    def network_configuration(self, print_response=False):

        with core_api.ApiClient(self.system_config) as api_client:
            api_client = self.set_basic_auth(api_client, "admin", "admin")
            try:
                api = network_api.NetworkApi(api_client)
                response: NetworkConfigurationResponse = api.network_configuration_post(dict())
                if print_response:
                    print(response)
                return response
            except ApiException as e:
                Helpers.handleApiException(e)

    def network_status(self, print_response=False):
        with core_api.ApiClient(self.system_config) as api_client:
            api_client = self.set_basic_auth(api_client, "admin", "admin")
            try:
                api = network_api.NetworkApi(api_client)
                response = api.network_status_post(
                    NetworkStatusRequest(self.network_configuration().network_identifier))
                if print_response:
                    print(response)
                return response
            except ApiException as e:
                Helpers.handleApiException(e)

    @staticmethod
    def set_validator_metadata(name, url):
        return lambda node_identifiers: [
            OperationGroup([
                Operation(
                    type="Data",
                    entity_identifier=node_identifiers.validator_entity_identifier,
                    data=Data(
                        action='CREATE',
                        data_object=ValidatorMetadata(
                            type="ValidatorMetadata",
                            name=name,
                            url=url
                        )
                    )
                )
            ]),
        ]

    @staticmethod
    def set_validator_registered(registered):
        return lambda node_identifiers: [
            OperationGroup([
                Operation(
                    type="Data",
                    entity_identifier=node_identifiers.validator_entity_identifier,
                    data=Data(
                        action='CREATE',
                        data_object=PreparedValidatorRegistered(
                            type="PreparedValidatorRegistered",
                            registered=registered
                        )
                    )
                )
            ])
        ]
