import os.path
import unittest
from monitoring import Monitoring


class MonitoringTests(unittest.TestCase):

    def test_template(self):
        Monitoring.template_dashboards(["dashboard.yml", "babylon-node-dashboard.json", "babylon-jvm-dashboard.json",
                                        "network-gateway-dashboard.json"], "/tmp")
        self.assertTrue(os.path.exists("/tmp/grafana/provisioning/dashboards/network-gateway-dashboard.json"))
        self.assertTrue(os.path.exists("/tmp/grafana/provisioning/dashboards/dashboard.yml"))
        self.assertTrue(os.path.exists("/tmp/grafana/provisioning/dashboards/babylon-jvm-dashboard.json"))
        self.assertTrue(os.path.exists("/tmp/grafana/provisioning/dashboards/network-gateway-dashboard.json"))


if __name__ == '__main__':
    unittest.main()
