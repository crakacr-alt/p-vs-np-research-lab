import unittest

from pnp_lab.cnf import parse_dimacs


class TestCNF(unittest.TestCase):
    def test_parse(self):
        problem = parse_dimacs(
            """
            c простой пример
            p cnf 3 2
            1 -2 3 0
            -1 2 0
            """
        )

        self.assertEqual(
            problem.variables,
            3,
        )

        self.assertEqual(
            len(problem.clauses),
            2,
        )

        self.assertEqual(
            problem.clauses[0],
            [1, -2, 3],
        )


if __name__ == "__main__":
    unittest.main()
