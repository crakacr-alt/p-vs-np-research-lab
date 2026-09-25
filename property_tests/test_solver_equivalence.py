import unittest

from hypothesis import given, settings, strategies as st

from pnp_lab.bruteforce import solve_bruteforce
from pnp_lab.cnf import CNFProblem, model_satisfies
from pnp_lab.hybrid import HybridSolver
from pnp_lab.switch_solver import RepresentationSwitchingSolver


@st.composite
def small_cnf(draw):
    variables = draw(st.integers(min_value=1, max_value=6))
    clause_count = draw(st.integers(min_value=0, max_value=14))
    clauses = []

    for _ in range(clause_count):
        width = draw(st.integers(min_value=0, max_value=min(3, variables)))
        clause = []

        for _ in range(width):
            variable = draw(st.integers(min_value=1, max_value=variables))
            positive = draw(st.booleans())
            clause.append(variable if positive else -variable)

        clauses.append(tuple(clause))

    return CNFProblem(
        variables=variables,
        clauses=tuple(clauses),
    )


class SolverEquivalenceProperties(unittest.TestCase):
    @settings(max_examples=100, deadline=None)
    @given(small_cnf())
    def test_exact_solvers_match_bruteforce(self, problem):
        expected_sat, _ = solve_bruteforce(problem)

        for solver in (HybridSolver(), RepresentationSwitchingSolver()):
            result = solver.solve(problem)

            self.assertEqual(
                result.sat,
                expected_sat,
                msg=f"{solver.name}: clauses={problem.clauses}",
            )

            if result.sat:
                self.assertTrue(model_satisfies(problem, result.model))


if __name__ == "__main__":
    unittest.main()
