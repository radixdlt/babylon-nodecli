from config.BaseConfig import BaseConfig


class DockerNginxConfig(BaseConfig):
    protect_gateway: str = "true"
    gateway_behind_auth: str = "true"
    enable_transaction_api = "false"
    protect_core: str = "true"
    release = None
    repo = "radixdlt/radixdlt-nginx"
