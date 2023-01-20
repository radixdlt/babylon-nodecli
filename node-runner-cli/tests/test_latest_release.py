import os
import unittest

from github.github import latest_release


# fill with valid token
token = "token <GH-TOKEN>"


class GitHubTests(unittest.TestCase):

    def legacy_test_latest_release(self):
        latest_release()

    def legacy_test_latest_release_nginx(self):
        latest_release("radixdlt/radixdlt-nginx")

    def legacy_test_latest_release_nodecli(self):
        latest_release("radixdlt/node-runner")

    def legacy_test_latest_release_gateway(self):
        latest_release("radixdlt/radixdlt-network-gateway")

    @unittest.skip("Waiting for first release in repo")
    def test_latest_release_node_with_auth(self):
        os.environ['GITHUB_TOKEN'] = token
        latest_release("radixdlt/babylon-node")

    def test_latest_release_nodecli_auth(self):
        os.environ['GITHUB_TOKEN'] = token
        latest_release("radixdlt/babylon-nodecli")

    def test_latest_release_nginx_with_auth(self):
        os.environ['GITHUB_TOKEN'] = token
        latest_release("radixdlt/babylon-nginx")

    def test_latest_release_nginx_environment_variable(self):
        os.environ['RADIXDTL_OVERRIDE_NGINX_VERSION'] = '1.3.3'
        version = latest_release("radixdlt/babylon-nginx")
        self.assertEqual(version, '1.3.3')

    def test_latest_release_cli_environment_variable(self):
        os.environ['RADIXDTL_OVERRIDE_CLI_VERSION'] = '1.3.3'
        version = latest_release("radixdlt/babylon-nodecli")
        self.assertEqual(version, '1.3.3')

    def test_latest_release_gateway_environment_variable(self):
        os.environ['RADIXDTL_OVERRIDE_GATEWAY_VERSION'] = '1.3.3'
        version = latest_release("radixdlt/babylon-nodecli")
        self.assertEqual(version, '1.3.3')

    @unittest.skip("This test is temporary until the repository goes public. waiting for first release in repo")
    def test_latest_release_gateway(self):
        latest_release("radixdlt/babylon-gateway")

    @unittest.skip("waiting for public repo")
    def test_latest_release_nginx(self):
        latest_release("radixdlt/babylon-nginx")

    @unittest.skip("waiting for public repo")
    def test_latest_release_nodecli(self):
        latest_release("radixdlt/babylon-nodecli")

    @unittest.skip("waiting for public repo")
    def test_latest_release_gateway(self):
        latest_release("radixdlt/babylon-gateway")


if __name__ == '__main__':
    unittest.main(warnings='ignore')
