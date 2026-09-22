import unittest

from pnp_lab.verification import cross_check_random


class TestVerification(unittest.TestCase):
    def test_baseline_and_hybrid_agree(self):
        summary = cross_check_random(
            variables=8,
            clauses=24,
            count=20,
            seed=10,
        )
        self.assertEqual(summary.baseline_vs_hybrid_mismatches, 0)


if __name__ == "__main__":
    unittest.main()
