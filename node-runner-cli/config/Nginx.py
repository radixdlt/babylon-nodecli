from config.BaseConfig import BaseConfig


class DockerNginxConfig(BaseConfig):
    mode: str = "docker"
    protect_gateway: str = "true"
    gateway_behind_auth: str = "true"
    enable_transaction_api = "false"
    protect_core: str = "true"
    release = None
    repo = "radixdlt/babylon-nginx"


class SystemdNginxConfig(BaseConfig):
    mode: str = "systemd"
    enable_transaction_api = "false"
    protect_core: str = "true"
    dir: str = '/etc/nginx'
    secrets_dir: str = '/etc/nginx/secrets'
    release: str = None
    config_url: str = None

    # def __init__(self, nginx_dir='/etc/nginx',
    #              nginx_secrets_dir='/etc/nginx/secrets',
    #              nginx_release=None,
    #              nginx_binary_url=None):
    #     self.dir = nginx_dir
    #     self.secrets_dir = nginx_secrets_dir
    #     self.release = nginx_release
    #     self.config_url = nginx_binary_url

    def __repr__(self):
        return "%s (dir=%r, secrets_dir=%r, release=%r, config_url=%r)" % (
            self.__class__.__name__, self.dir, self.secrets_dir,
            self.release, self.config_url)
