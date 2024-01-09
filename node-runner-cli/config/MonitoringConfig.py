from urllib.parse import urlparse

from config.BaseConfig import BaseConfig, SetupMode
from utils.Prompts import Prompts
from utils.utils import Helpers


class CommonMonitoringConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.docker_compose_file = (
            f"{Helpers.get_default_monitoring_config_dir()}/node-monitoring.yml"
        )
        self.config_dir = Helpers.get_default_monitoring_config_dir()
        super().__init__(config_dict)


class PrometheusConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.metrics_path = "/metrics"
        self.metrics_target = "localhost"
        self.basic_auth_password = ""
        self.basic_auth_user = ""
        self.scheme = "https"
        super().__init__(config_dict)

    def ask_prometheus_target(self, basic_auth_password, target_name):
        self.metrics_target = f"{Helpers.get_node_host_ip()}"
        if "DETAILED" in SetupMode.instance().mode:
            url = Prompts.ask_metrics_target_details(
                target_name, f"https://{self.metrics_target}"
            )
            self.set_target_details(url, target_name)

        elif self.scheme == "https":
            self.basic_auth_user = "metrics"
            if not basic_auth_password:
                self.basic_auth_password = Prompts.ask_basic_auth_password(
                    self.basic_auth_user, target_name
                )
            else:
                self.basic_auth_password = basic_auth_password

    def set_target_details(self, url, target_name):
        parsed_url = urlparse(url)
        self.scheme = parsed_url.scheme
        self.metrics_target = (
            f"{parsed_url.hostname}:{parsed_url.port}"
            if parsed_url.port
            else f"{parsed_url.hostname}"
        )
        if parsed_url.scheme == "https":
            auth = Prompts.ask_basic_auth(target_name, "metrics")
            self.basic_auth_password = auth["password"]
            self.basic_auth_user = auth["name"]


class MonitoringConfig(BaseConfig):
    def __init__(self, config_dict: dict):
        if config_dict is None:
            config_dict = dict()
        self.monitor_core: PrometheusConfig = PrometheusConfig(
            config_dict.get("monitor_core")
        )
        self.monitor_gateway_api: PrometheusConfig = PrometheusConfig(
            config_dict.get("monitor_gateway_api")
        )
        self.monitor_aggregator: PrometheusConfig = PrometheusConfig(
            config_dict.get("monitor_aggregator")
        )
        self.common_config: CommonMonitoringConfig = CommonMonitoringConfig(
            config_dict.get("common_config")
        )
        super().__init__(config_dict)

    def configure_core_target(self, basic_auth_password):
        self.monitor_core.ask_prometheus_target(
            basic_auth_password, target_name="CORE_NODE"
        )
        self.monitor_core.metrics_path = "/prometheus/metrics"

    def configure_gateway_api_target(self, basic_auth_password):
        self.monitor_gateway_api.ask_prometheus_target(
            basic_auth_password, target_name="GATEWAY_API"
        )
        self.monitor_gateway_api.metrics_path = "/gateway/metrics"

    def configure_aggregator_target(self, basic_auth_password):
        self.monitor_aggregator.ask_prometheus_target(
            basic_auth_password, target_name="AGGREGATOR"
        )
        self.monitor_aggregator.metrics_path = "/aggregator/metrics"
