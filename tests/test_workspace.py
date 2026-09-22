import os
import tempfile
import unittest
from pathlib import Path

from pnp_lab.workspace import safe_workspace_path


class TestWorkspace(unittest.TestCase):
    def test_path_inside_workspace_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            old_value = os.environ.get("PNP_LAB_WORKSPACE")
            os.environ["PNP_LAB_WORKSPACE"] = directory

            try:
                result = safe_workspace_path("results/test.cnf")
                self.assertTrue(
                    str(result).startswith(str(Path(directory).resolve()))
                )
            finally:
                if old_value is None:
                    os.environ.pop("PNP_LAB_WORKSPACE", None)
                else:
                    os.environ["PNP_LAB_WORKSPACE"] = old_value

    def test_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            old_value = os.environ.get("PNP_LAB_WORKSPACE")
            os.environ["PNP_LAB_WORKSPACE"] = directory

            try:
                with self.assertRaises(ValueError):
                    safe_workspace_path("../outside.txt")
            finally:
                if old_value is None:
                    os.environ.pop("PNP_LAB_WORKSPACE", None)
                else:
                    os.environ["PNP_LAB_WORKSPACE"] = old_value


if __name__ == "__main__":
    unittest.main()
