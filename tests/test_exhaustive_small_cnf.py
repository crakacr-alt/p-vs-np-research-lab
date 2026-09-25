import unittest
from itertools import product

from pnp_lab.bruteforce import solve_bruteforce
from pnp_lab.cnf import CNFProblem
from pnp_lab.switch_solver import RepresentationSwitchingSolver


class ExhaustiveSmallCNFTests(unittest.TestCase):
    def test_all_three_variable_full_width_clause_subsets_match_bruteforce(self):
        """Проверяем все 2^8 формулы из возможных 3-литеральных клауз.

        Для трёх переменных существует восемь комбинаций знаков в клаузе
        длины три. Любое подмножество этих восьми клауз — отдельная CNF-формула.
        Полный перебор всех 256 подмножеств дешёвый и хорошо ловит ошибки в
        распознавании XOR-блоков и representation switching.
        """

        possible_clauses = [
            tuple(index + 1 if sign else -(index + 1) for index, sign in enumerate(signs))
            for signs in product((False, True), repeat=3)
        ]

        solver = RepresentationSwitchingSolver()

        for mask in range(1 << len(possible_clauses)):
            clauses = tuple(
                clause
                for index, clause in enumerate(possible_clauses)
                if mask & (1 << index)
            )
            problem = CNFProblem(variables=3, clauses=clauses)

            expected_sat, _ = solve_bruteforce(problem)
            actual = solver.solve(problem)

            self.assertEqual(
                actual.sat,
                expected_sat,
                msg=f"mask={mask}, clauses={clauses}",
            )


if __name__ == "__main__":
    unittest.main()
