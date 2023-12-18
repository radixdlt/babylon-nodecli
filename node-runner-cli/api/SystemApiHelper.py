from api.Api import API
from api.CustomAPIClient import CustomAPIClient
from utils.utils import Helpers


class SystemApiHelper(API):
    node_host = None
    api_client = None
    network_identified = None

    def __init__(self, user_type="admin", default_username="admin"):
        self.node_host = API.get_host_info()
        self.api_client: CustomAPIClient = CustomAPIClient(
            host=self.node_host, verify_ssl=False
        )
        self.api_client = self.set_basic_auth(
            self.api_client, user_type, default_username
        )

    def health(self, print_response=False):
        self.api_client.prepare("GET", "/system/health")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )

    def version(self, print_response=False):
        self.api_client.prepare("GET", "/system/version")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )

    def configuration(self, print_response=False):
        self.api_client.prepare("GET", "/system/configuration")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )

    def peers(self, print_response=False):
        self.api_client.prepare("GET", "/system/peers")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )

    def addressbook(self, print_response=False):
        self.api_client.prepare("GET", "/system/addressbook")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )

    def network_sync_status(self, print_response=False):
        self.api_client.prepare("GET", "/system/network-sync-status")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )

    def prometheus_metrics(self, print_response=False):
        self.api_client.prepare("GET", "/prometheus/metrics")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )

    def identity(self, print_response=False):
        self.api_client.prepare("GET", "/system/identity")
        Helpers.send_request(
            self.api_client.prepared_req,
            print_request=False,
            print_response=print_response,
        )
