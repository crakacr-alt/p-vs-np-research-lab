import unittest

from pnp_lab.decomposition import split_into_independent_components


class TestDecomposition(unittest.TestCase):
    def test_two_components(self):
        clauses = [
            [1, 2],
            [-1, 2],
            [10, 11],
            [-10, 11],
        ]

        components = split_into_independent_components(clauses)
        sizes = sorted(len(component) for component in components)
        self.assertEqual(sizes, [2, 2])


if __name__ == "__main__":
    unittest.main()
