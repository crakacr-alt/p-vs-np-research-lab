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

    def test_chain_of_shared_variables_stays_one_component(self):
        clauses = [
            [1, 2],
            [2, 3],
            [3, 4],
            [4, 5],
        ]

        components = split_into_independent_components(clauses)

        self.assertEqual(len(components), 1)
        self.assertEqual(len(components[0]), 4)

    def test_many_clauses_on_same_variable_do_not_duplicate(self):
        clauses = [[1, index] for index in range(2, 102)]

        components = split_into_independent_components(clauses)

        self.assertEqual(len(components), 1)
        self.assertEqual(len(components[0]), 100)

    def test_empty_input_keeps_previous_contract(self):
        self.assertEqual(split_into_independent_components([]), [[]])


if __name__ == "__main__":
    unittest.main()
