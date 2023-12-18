import unittest
from unittest.mock import patch

from babylonnode import main


class EulaTests(unittest.TestCase):
    def test_eula_can_be_executed(self):
        with patch("sys.argv", ["main", "eula"]):
            main()
