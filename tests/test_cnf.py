import tempfile
import unittest
from pathlib import Path

from pnp_lab.cnf import CNFProblem, load_dimacs, model_satisfies, save_dimacs


class TestCNF(unittest.TestCase):
    def test_round_trip_dimacs(self):
        problem = CNFProblem(
            variables=3,
            clauses=((1, -2, 3), (-1, 2)),
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.cnf"
            save_dimacs(problem, path)
            loaded = load_dimacs(path)

        self.assertEqual(problem, loaded)

    def test_model_check(self):
        problem = CNFProblem(
            variables=2,
            clauses=((1, 2), (-1, 2)),
        )

        self.assertTrue(model_satisfies(problem, {1: False, 2: True}))
        self.assertFalse(model_satisfies(problem, {1: False, 2: False}))


if __name__ == "__main__":
    unittest.main()
