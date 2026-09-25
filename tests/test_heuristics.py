import unittest

from pnp_lab.heuristics import choose_jw_branch


class TestBranchingHeuristic(unittest.TestCase):
    def test_short_clause_has_more_weight(self):
        clauses = [
            [2, 3],
            [1, 4, 5, 6, 7],
            [1, 8, 9, 10, 11],
            [1, 12, 13, 14, 15],
        ]

        variable, _ = choose_jw_branch(clauses)

        # Простая частота выбрала бы 1. Jeroslow-Wang выбирает 2 или 3,
        # потому что двухлитеральная клауза сильнее ограничивает поиск.
        self.assertIn(variable, {2, 3})

    def test_preferred_polarity_uses_literal_scores(self):
        clauses = [
            [-1, 2],
            [-1, 3],
            [1, 4, 5],
        ]

        variable, preferred = choose_jw_branch(clauses)

        self.assertEqual(variable, 1)
        self.assertFalse(preferred)

    def test_extra_groups_can_add_xor_only_variable(self):
        variable, preferred = choose_jw_branch([], [(7, 8, 9)])

        self.assertEqual(variable, 7)
        self.assertTrue(preferred)


if __name__ == "__main__":
    unittest.main()
