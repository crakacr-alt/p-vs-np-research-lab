from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class XORTransformationCertificate:
    """Проверяемое свидетельство замены CNF-блока на XOR-уравнение."""

    variables: tuple[int, ...]
    rhs: bool
    source_clauses: tuple[tuple[int, ...], ...]


def _literal_value(literal: int, assignment: dict[int, bool]) -> bool:
    value = assignment[abs(literal)]
    return value if literal > 0 else not value


def verify_xor_certificate(certificate: XORTransformationCertificate) -> bool:
    """Независимо проверяет эквивалентность source_clauses и XOR truth table.

    Проверка намеренно не использует detect_xor3 или xor3_to_cnf.
    Для XOR3 полный truth table содержит всего восемь присваиваний.
    """

    variables = certificate.variables

    if len(variables) != 3 or len(set(variables)) != 3:
        return False

    variable_set = set(variables)
    if any(
        len(clause) != 3
        or {abs(literal) for literal in clause} != variable_set
        for clause in certificate.source_clauses
    ):
        return False

    for bits in product([False, True], repeat=3):
        assignment = dict(zip(variables, bits))

        cnf_value = all(
            any(_literal_value(literal, assignment) for literal in clause)
            for clause in certificate.source_clauses
        )
        xor_value = (sum(int(assignment[variable]) for variable in variables) % 2) == int(
            certificate.rhs
        )

        if cnf_value != xor_value:
            return False

    return True
