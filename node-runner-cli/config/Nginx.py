from config.BaseConfig import BaseConfig


class DockerNginxConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.mode: str = "docker"
        self.protect_gateway: str = "true"
        self.gateway_behind_auth: str = "true"
        self.protect_core: str = "true"
        self.release = ""
        self.repo = "radixdlt/babylon-nginx"
        self.mode = "docker"
        super().__init__(config_dict)


class SystemdNginxConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.mode: str = "systemd"
        self.protect_core: str = "true"
        self.dir: str = '/etc/nginx'
        self.secrets_dir: str = '/etc/nginx/secrets'
        self.release: str = ""
        self.config_url: str = ""
        self.mode = "systemd"
        super().__init__(config_dict)
