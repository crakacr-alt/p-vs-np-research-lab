import unittest

from pnp_lab.cnf import model_satisfies
from pnp_lab.generator import planted_3sat, random_3sat


class TestGenerator(unittest.TestCase):
    def test_random_is_reproducible(self):
        first = random_3sat(10, 20, seed=123)
        second = random_3sat(10, 20, seed=123)
        self.assertEqual(first, second)

    def test_planted_model_really_satisfies(self):
        problem, model = planted_3sat(10, 30, seed=7)
        self.assertTrue(model_satisfies(problem, model))


if __name__ == "__main__":
    unittest.main()
