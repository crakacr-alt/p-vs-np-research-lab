import unittest

from pnp_lab.certificates import XORTransformationCertificate, verify_xor_certificate
from pnp_lab.xor import XOREquation, xor3_to_cnf


class TransformationCertificateTests(unittest.TestCase):
    def test_valid_xor_certificate(self):
        equation = XOREquation((1, 2, 3), True)
        certificate = XORTransformationCertificate(
            variables=equation.variables,
            rhs=equation.rhs,
            source_clauses=xor3_to_cnf(equation),
        )
        self.assertTrue(verify_xor_certificate(certificate))

    def test_modified_clause_is_rejected(self):
        equation = XOREquation((1, 2, 3), False)
        clauses = list(xor3_to_cnf(equation))
        clauses[0] = (1, 2, 3)

        certificate = XORTransformationCertificate(
            variables=equation.variables,
            rhs=equation.rhs,
            source_clauses=tuple(clauses),
        )
        self.assertFalse(verify_xor_certificate(certificate))


if __name__ == "__main__":
    unittest.main()
