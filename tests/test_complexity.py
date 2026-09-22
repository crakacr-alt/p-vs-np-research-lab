import unittest

from pnp_lab.complexity import fit_exponential, fit_polynomial


class TestComplexity(unittest.TestCase):
    def test_polynomial_fit(self):
        ns = [2, 3, 4, 5, 6]
        costs = [n**3 for n in ns]
        result = fit_polynomial(ns, costs)
        self.assertAlmostEqual(result.parameter, 3.0, places=6)
        self.assertGreater(result.score_r2, 0.999)

    def test_exponential_fit(self):
        ns = [1, 2, 3, 4, 5]
        costs = [2**n for n in ns]
        result = fit_exponential(ns, costs)
        self.assertAlmostEqual(result.parameter, 2.0, places=6)
        self.assertGreater(result.score_r2, 0.999)


if __name__ == "__main__":
    unittest.main()
