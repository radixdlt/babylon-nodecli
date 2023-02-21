import os.path
import unittest
from monitoring import Monitoring

class MyTestCase(unittest.TestCase):

    def test_template(self):
        Monitoring.template_dashboards(["dashboard.yml", "babylon-node-dashboard.json", "babylon-jvm-dashboard.json",
                                        "network-gateway-dashboard.json"], "/tmp")
        self.assertTrue(os.path.exists("/tmp/grafana/provisioning/dashboards/network-gateway-dashboard.json"))

if __name__ == '__main__':
    unittest.main()
