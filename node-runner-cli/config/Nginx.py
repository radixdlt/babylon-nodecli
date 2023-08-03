from config.BaseConfig import BaseConfig


class DockerNginxConfig(BaseConfig):
    mode: str = "docker"
    protect_gateway: str = "true"
    gateway_behind_auth: str = "true"
    enable_transaction_api = "false"
    protect_core: str = "true"
    release = None
    repo = "radixdlt/babylon-nginx"

    def __init__(self, config_dict: dict):
        self.mode = "docker"
        super().__init__(config_dict)


class SystemdNginxConfig(BaseConfig):
    mode: str = "systemd"
    enable_transaction_api = "false"
    protect_core: str = "true"
    dir: str = '/etc/nginx'
    secrets_dir: str = '/etc/nginx/secrets'
    release: str = None
    config_url: str = None

    def __init__(self, config_dict: dict):
        self.mode = "systemd"
        super().__init__(config_dict)

    def __repr__(self):
        return "%s (dir=%r, secrets_dir=%r, release=%r, config_url=%r)" % (
            self.__class__.__name__, self.dir, self.secrets_dir,
            self.release, self.config_url)
