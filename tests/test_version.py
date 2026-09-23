import importlib.metadata
import unittest

import pnp_lab


class TestPackageVersion(unittest.TestCase):
    def test_package_and_module_versions_match(self):
        installed = importlib.metadata.version("p-vs-np-research-lab")
        self.assertEqual(installed, pnp_lab.__version__)
        self.assertEqual(installed, "1.1.0")


if __name__ == "__main__":
    unittest.main()
