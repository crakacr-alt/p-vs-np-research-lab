import unittest

from pnp_lab.cnf import CNFProblem
from pnp_lab.cnf import model_satisfies
from pnp_lab.dpll import DPLLSolver


class TestSolver(unittest.TestCase):
    def test_sat(self):
        problem = CNFProblem(
            variables=2,
            clauses=[
                [1, 2],
                [-1, 2],
            ],
        )

        result = DPLLSolver().solve(
            problem
        )

        self.assertTrue(
            result.sat
        )

        self.assertTrue(
            model_satisfies(
                problem,
                result.model,
            )
        )

    def test_unsat(self):
        problem = CNFProblem(
            variables=1,
            clauses=[
                [1],
                [-1],
            ],
        )

        result = DPLLSolver().solve(
            problem
        )

        self.assertFalse(
            result.sat
        )


if __name__ == "__main__":
    unittest.main()
