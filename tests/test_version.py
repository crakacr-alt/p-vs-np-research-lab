import importlib.metadata
import unittest

import pnp_lab


class TestPackageVersion(unittest.TestCase):
    def test_package_and_module_versions_match(self):
        try:
            installed = importlib.metadata.version("p-vs-np-research-lab")
        except importlib.metadata.PackageNotFoundError:
            self.skipTest(
                "distribution metadata is unavailable; install with 'pip install -e .' "
                "to verify package metadata"
            )

        self.assertEqual(installed, pnp_lab.__version__)
        self.assertEqual(installed, "1.1.0")


if __name__ == "__main__":
    unittest.main()
