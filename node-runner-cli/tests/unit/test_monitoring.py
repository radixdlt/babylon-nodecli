import os.path
import unittest
from io import StringIO
from json import loads
from unittest import mock

from jinja2.exceptions import TemplateNotFound

from babylonnode import main
from monitoring.monitoring import Monitoring


class MonitoringTests(unittest.TestCase):
    def test_render_grafana_templates(self):
        Monitoring.template_dashboards(["babylon-node-dashboard.json"], "/tmp")
        dashboard = loads(
            open(
                "/tmp/grafana/provisioning/dashboards/babylon-node-dashboard.json"
            ).read()
        )
        self.assertEqual(
            dashboard["panels"][0]["targets"][0]["legendFormat"], "{{ health }}"
        )

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_template(self, mock_stdout):
        Monitoring.template_dashboards(
            [
                "dashboard.yml",
                "babylon-node-dashboard.json",
                "babylon-jvm-dashboard.json",
                "network-gateway-dashboard.json",
            ],
            "/tmp",
        )
        self.assertTrue(
            os.path.exists(
                "/tmp/grafana/provisioning/dashboards/network-gateway-dashboard.json"
            )
        )
        self.assertTrue(
            os.path.exists("/tmp/grafana/provisioning/dashboards/dashboard.yml")
        )
        self.assertTrue(
            os.path.exists(
                "/tmp/grafana/provisioning/dashboards/babylon-jvm-dashboard.json"
            )
        )
        self.assertTrue(
            os.path.exists(
                "/tmp/grafana/provisioning/dashboards/network-gateway-dashboard.json"
            )
        )

    @unittest.skip("endless loop")
    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_template_failure(self, mock_stdout):
        with self.assertRaises(TemplateNotFound) as cm:
            Monitoring.template_dashboards(["this-template-does-not-exist"], "/tmp")
            self.assertEqual(
                mock_stdout.getvalue(),
                "jinja2.exceptions.TemplateNotFound: this-template-does-not-exist.j2",
            )
            self.assertEqual(cm.exception.code, 1)

    @unittest.skip("endless loop")
    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_monitoring_config(self, mock_out):
        with mock.patch(
            "builtins.input",
            side_effect=["Y", "https://45.152.180.182", "metrics", "testpassword", "n"],
        ):
            with mock.patch("sys.argv", ["main", "monitoring", "config"]):
                main()

        with mock.patch(
            "sys.argv",
            ["main", "monitoring", "config", "-m", "MONITOR_CORE", "-cm", "test"],
        ):
            main()

        with mock.patch(
            "builtins.input",
            side_effect=["Y", "https://45.152.180.182", "metrics", "testpassword", "n"],
        ):
            with mock.patch(
                "sys.argv", ["main", "monitoring", "config", "-m", "DETAILED"]
            ):
                main()

    # def test_monitoring_config_tofile(self):
    #     config = MonitoringConfig({})
    #     self.maxDiff = None
    #     # self.assertEqual("", config.to_dict())
    #     # self.assertEqual("", config.to_yaml())
    #     # config.to_file("/tmp/test")


if __name__ == "__main__":
    unittest.main()
