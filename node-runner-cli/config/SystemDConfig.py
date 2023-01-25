from config.BaseConfig import BaseConfig
from config.KeyDetails import KeyDetails
from config.Nginx import SystemdNginxConfig
from utils.utils import Helpers


class SystemDSettings(BaseConfig):
    nginx: SystemdNginxConfig
    service_user: str
    data_directory: str
    host_ip: str
    node_type: str
    node_dir: str
    node_secrets_dir: str
    node_version: str
    core_release: str
    core_binary_url: str
    enable_transaction: str
    trusted_node: str
    keydetails: KeyDetails
    java_opts: str

    def __iter__(self):
        class_variables = {key: value
                           for key, value in self.__class__.__dict__.items()
                           if not key.startswith('__') and not callable(value)}
        for attr, value in class_variables.items():
            if attr in ['keydetails']:
                yield attr, dict(self.__getattribute__(attr))
            elif self.__getattribute__(attr):
                yield attr, self.__getattribute__(attr)

    def __init__(self,
                 service_user="radixdlt",
                 data_directory=f"{Helpers.get_home_dir()}/data",
                 host_ip=None,
                 node_type="fullnode",
                 node_dir='/etc/radixdlt/node',
                 node_secrets_dir='/etc/radixdlt/node/secrets',
                 node_version=None,
                 nginx_settings=SystemdNginxConfig(),
                 core_release=None,
                 core_binary_url="radixdlt/radixdlt-core",
                 enable_transaction="false",
                 trusted_node=None,
                 keydetails=KeyDetails({}),
                 java_opts="--enable-preview -server -Xms8g -Xmx8g  " \
                           "-XX:MaxDirectMemorySize=2048m " \
                           "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops " \
                           "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts " \
                           "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom " \
                           "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"):
        self.nginx = nginx_settings
        self.service_user = service_user
        self.data_directory = data_directory
        self.host_ip = host_ip
        self.node_type = node_type
        self.node_dir = node_dir
        self.node_secrets_dir = node_secrets_dir
        self.node_version = node_version

        self.core_release = core_release
        self.core_binary_url = core_binary_url
        self.enable_transaction = enable_transaction
        self.trusted_node = trusted_node
        self.keydetails = keydetails
        self.java_opts = java_opts

    def __repr__(self):
        return "%s (service_user=%r, data_directory=%r, host_ip=%r, node_type=%r, node_dir=%r, node_secrets_dir=%r, " \
               "node_version=%r, nginx_dir=%r, nginx_secrets_dir=%r, nginx_release=%r, nginx_binary_url=%r, " \
               "core_release=%r, core_binary_url=%r, enable_transaction=%r, trusted_node=%r, keydetails=%r, " \
               "java_opts=%r)" % (
            self.__class__.__name__, self.service_user, self.data_directory, self.host_ip, self.node_type,
            self.node_dir, self.node_secrets_dir, self.node_version, self.nginx_dir, self.nginx_secrets_dir,
            self.nginx_release, self.nginx_binary_url, self.core_release, self.core_binary_url,
            self.enable_transaction, self.trusted_node, self.keydetails, self.java_opts)
