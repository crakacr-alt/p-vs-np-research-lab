import unittest

from pnp_lab.generator import random_3sat


class TestGenerator(unittest.TestCase):
    def test_same_seed_same_formula(self):
        first = random_3sat(
            variables=10,
            clauses=20,
            seed=123,
        )

        second = random_3sat(
            variables=10,
            clauses=20,
            seed=123,
        )

        self.assertEqual(
            first.clauses,
            second.clauses,
        )

    def test_every_clause_has_three_variables(self):
        problem = random_3sat(
            variables=10,
            clauses=20,
            seed=1,
        )

        for clause in problem.clauses:
            self.assertEqual(
                len(clause),
                3,
            )


if __name__ == "__main__":
    unittest.main()
