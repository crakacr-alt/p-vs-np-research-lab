import unittest

from pnp_lab.cnf import CNFProblem, model_satisfies
from pnp_lab.dpll import DPLLSolver
from pnp_lab.hybrid import HybridSolver


class TestSolvers(unittest.TestCase):
    def setUp(self):
        self.sat_problem = CNFProblem(
            variables=3,
            clauses=((1, 2), (-1, 3), (-2, 3)),
        )
        self.unsat_problem = CNFProblem(
            variables=1,
            clauses=((1,), (-1,)),
        )

    def test_baseline_sat(self):
        result = DPLLSolver().solve(self.sat_problem)
        self.assertTrue(result.sat)
        self.assertTrue(model_satisfies(self.sat_problem, result.model))

    def test_baseline_unsat(self):
        self.assertFalse(DPLLSolver().solve(self.unsat_problem).sat)

    def test_hybrid_sat(self):
        result = HybridSolver().solve(self.sat_problem)
        self.assertTrue(result.sat)
        self.assertTrue(model_satisfies(self.sat_problem, result.model))

    def test_hybrid_unsat(self):
        self.assertFalse(HybridSolver().solve(self.unsat_problem).sat)


if __name__ == "__main__":
    unittest.main()
