from config.BaseConfig import BaseConfig


class DockerNginxConfig(BaseConfig):
    mode: str = "docker"
    protect_gateway: str = "true"
    gateway_behind_auth: str = "true"
    enable_transaction_api = "false"
    protect_core: str = "true"
    release = None
    repo = "radixdlt/babylon-nginx"

    def __init__(self, settings: dict):
        self.mode = "docker"
        self.protect_gateway = "true" if settings.get("protect_gateway") is None else settings.get("protect_gateway")
        self.gateway_behind_auth = "true" if settings.get("gateway_behind_auth") is None else settings.get(
            "gateway_behind_auth")
        self.enable_transaction_api = "false" if settings.get("enable_transaction_api") is None else settings.get(
            "enable_transaction_api")
        self.protect_core = "true" if settings.get("protect_core") is None else settings.get("protect_core")
        self.repo = "radixdlt/babylon-nginx" if settings.get("repo") is None else settings.get("repo")
        self.release = settings.get("release")


class SystemdNginxConfig(BaseConfig):
    mode: str = "systemd"
    enable_transaction_api = "false"
    protect_core: str = "true"
    dir: str = '/etc/nginx'
    secrets_dir: str = '/etc/nginx/secrets'
    release: str = None
    config_url: str = None

    def __init__(self, settings: dict):
        super().__init__(settings)

    def __repr__(self):
        return "%s (dir=%r, secrets_dir=%r, release=%r, config_url=%r)" % (
            self.__class__.__name__, self.dir, self.secrets_dir,
            self.release, self.config_url)
