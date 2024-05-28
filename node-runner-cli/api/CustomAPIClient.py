import requests
from requests.models import PreparedRequest


class CustomAPIClient:
    prepared_req: PreparedRequest = None

    def __init__(self, host=None, verify_ssl=True):
        """Default Base url"""
        self._base_path = "http://localhost:3333" if host is None else host

        self.verify_ssl = verify_ssl

        self.user_agent = "Babylon babylonnode cli"
        self.default_headers = {}
        self.set_default_header("User-Agent", self.user_agent)

    def set_default_header(self, header_name, header_value):
        self.default_headers[header_name] = header_value

    def prepare(
        self,
        http_method,
        http_path,
    ):
        req = requests.Request(
            http_method, f"{self._base_path}{http_path}", headers=self.default_headers
        )
        self.prepared_req = req.prepare()
