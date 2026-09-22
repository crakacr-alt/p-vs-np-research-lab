import unittest

from pnp_lab.benchmark_runner import run_release_suite


class TestReleaseBenchmarks(unittest.TestCase):
    def test_release_suite_has_consistent_answers(self):
        results = run_release_suite(seed=1)

        self.assertGreater(len(results), 0)

        for row in results:
            if row.expected_sat is not None:
                self.assertTrue(
                    row.matches_expected,
                    msg=f"{row.case} / {row.solver}",
                )

    def test_switch_activates_on_xor_family(self):
        results = run_release_suite(seed=1)
        xor_switch_rows = [
            row
            for row in results
            if row.family == "xor" and row.solver == "representation-switch-v1"
        ]

        self.assertGreater(len(xor_switch_rows), 0)

        for row in xor_switch_rows:
            self.assertGreater(row.xor_equations_detected, 0)
            self.assertGreater(row.representation_switches, 0)


if __name__ == "__main__":
    unittest.main()
