import unittest

from pnp_lab.bruteforce import solve_bruteforce
from pnp_lab.generator import random_3sat
from pnp_lab.switch_solver import RepresentationSwitchingSolver


class TestBruteforceOracle(unittest.TestCase):
    def test_switch_matches_bruteforce_on_small_random_formulas(self):
        for seed in range(20):
            problem = random_3sat(
                variables=6,
                clauses=20,
                seed=seed,
            )

            brute_sat, _ = solve_bruteforce(problem)
            switch_sat = RepresentationSwitchingSolver().solve(problem).sat

            self.assertEqual(
                brute_sat,
                switch_sat,
                msg=f"Несовпадение на seed={seed}",
            )


if __name__ == "__main__":
    unittest.main()
