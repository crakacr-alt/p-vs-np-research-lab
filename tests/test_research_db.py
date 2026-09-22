import tempfile
import unittest
from pathlib import Path

from pnp_lab.research_db import ResearchDatabase


class TestResearchDatabase(unittest.TestCase):
    def test_hypothesis_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "research.db"
            database = ResearchDatabase(path)
            hypothesis_id = database.add_hypothesis(
                "Тест",
                "Проверяемое утверждение",
            )
            database.set_status(hypothesis_id, "TESTING")
            items = database.list_hypotheses()

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].status, "TESTING")


if __name__ == "__main__":
    unittest.main()
