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

        # Версия в pyproject и версия, которую показывает сам модуль, должны
        # совпадать. Конкретное число здесь не фиксируем, иначе каждый релиз
        # требует менять один и тот же номер ещё и в тесте.
        self.assertEqual(installed, pnp_lab.__version__)


if __name__ == "__main__":
    unittest.main()
