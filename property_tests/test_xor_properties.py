import unittest

from hypothesis import given, strategies as st

from pnp_lab.cnf import CNFProblem
from pnp_lab.xor import XOREquation, detect_xor3_with_certificates, xor3_to_cnf


@st.composite
def xor_cases(draw):
    variables = tuple(sorted(draw(st.sets(st.integers(1, 30), min_size=3, max_size=3))))
    rhs = draw(st.booleans())
    equation = XOREquation(variables=variables, rhs=rhs)

    clauses = list(xor3_to_cnf(equation))
    order = draw(st.permutations(tuple(range(4))))
    reverse_literals = draw(st.lists(st.booleans(), min_size=4, max_size=4))

    shuffled = []
    for position, index in enumerate(order):
        clause = clauses[index]
        if reverse_literals[position]:
            clause = tuple(reversed(clause))
        shuffled.append(clause)

    return equation, CNFProblem(variables=max(variables), clauses=tuple(shuffled))


class XORPropertyTests(unittest.TestCase):
    @given(xor_cases())
    def test_detector_preserves_random_xor3_truth_table(self, case):
        expected, problem = case
        remaining, equations, certificates = detect_xor3_with_certificates(problem)

        self.assertEqual(remaining.clauses, ())
        self.assertEqual(equations, (expected,))
        self.assertEqual(len(certificates), 1)


if __name__ == "__main__":
    unittest.main()
