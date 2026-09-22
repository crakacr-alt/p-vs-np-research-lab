import unittest

from pnp_lab.hard_search import search_hard_case


class TestHardSearch(unittest.TestCase):
    def test_returns_problem(self):
        case = search_hard_case(
            variables=6,
            clauses=12,
            iterations=5,
            seed=1,
        )
        self.assertEqual(case.problem.variables, 6)
        self.assertEqual(len(case.problem.clauses), 12)


if __name__ == "__main__":
    unittest.main()
