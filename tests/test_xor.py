import unittest
from itertools import product

from pnp_lab.benchmarks import xor_chain, xor_inconsistent_core
from pnp_lab.cnf import CNFProblem, model_satisfies
from pnp_lab.switch_solver import RepresentationSwitchingSolver
from pnp_lab.xor import XOREquation, detect_xor3, xor3_to_cnf


class TestXORRepresentation(unittest.TestCase):
    def test_xor3_encoding_matches_parity(self):
        equation = XOREquation((1, 2, 3), True)
        problem = CNFProblem(
            variables=3,
            clauses=xor3_to_cnf(equation),
        )

        for values in product([False, True], repeat=3):
            model = {
                1: values[0],
                2: values[1],
                3: values[2],
            }
            expected = values[0] ^ values[1] ^ values[2]
            self.assertEqual(
                model_satisfies(problem, model),
                expected,
            )

    def test_detector_recovers_xor(self):
        equation = XOREquation((1, 2, 3), False)
        problem = CNFProblem(
            variables=3,
            clauses=xor3_to_cnf(equation),
        )

        remaining, equations = detect_xor3(problem)

        self.assertEqual(remaining.clauses, ())
        self.assertEqual(equations, (equation,))

    def test_switch_solver_solves_xor_chain_without_branching(self):
        problem = xor_chain(8)
        result = RepresentationSwitchingSolver().solve(problem)

        self.assertTrue(result.sat)
        self.assertEqual(result.metrics.xor_equations_detected, 8)
        self.assertGreaterEqual(result.metrics.representation_switches, 1)
        self.assertEqual(result.metrics.decisions, 0)
        self.assertTrue(model_satisfies(problem, result.model))

    def test_inconsistent_xor_core_is_unsat(self):
        problem = xor_inconsistent_core()
        result = RepresentationSwitchingSolver().solve(problem)

        self.assertFalse(result.sat)
        self.assertEqual(result.metrics.xor_equations_detected, 4)


    def test_incomplete_xor_block_is_not_extracted(self):
        equation = XOREquation((1, 2, 3), True)
        incomplete = xor3_to_cnf(equation)[:3]
        problem = CNFProblem(
            variables=3,
            clauses=incomplete,
        )

        remaining, equations = detect_xor3(problem)

        self.assertEqual(equations, ())
        self.assertEqual(remaining, problem)

    def test_mixed_cnf_and_xor_matches_bruteforce(self):
        from pnp_lab.bruteforce import solve_bruteforce

        clauses = []
        clauses.extend(
            xor3_to_cnf(
                XOREquation((1, 2, 3), True)
            )
        )
        clauses.extend(
            xor3_to_cnf(
                XOREquation((3, 4, 5), False)
            )
        )
        clauses.extend(
            [
                (1,),
                (-5, 6),
            ]
        )

        problem = CNFProblem(
            variables=6,
            clauses=tuple(clauses),
        )

        brute_sat, _ = solve_bruteforce(problem)
        switched = RepresentationSwitchingSolver().solve(problem)

        self.assertEqual(switched.sat, brute_sat)

        if switched.sat:
            self.assertTrue(
                model_satisfies(problem, switched.model)
            )

        self.assertEqual(
            switched.metrics.xor_equations_detected,
            2,
        )


if __name__ == "__main__":
    unittest.main()
