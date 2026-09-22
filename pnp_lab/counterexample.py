from dataclasses import dataclass

from .dpll import DPLLSolver
from .generator import random_3sat


@dataclass
class HardCase:
    seed: int
    variables: int
    clauses: int
    sat: bool
    decisions: int
    calls: int
    seconds: float


def find_hard_random_case(
    variables,
    tries,
    ratio=4.2,
    seed_start=1,
):
    """Ищет случайную формулу, на которой DPLL сделал больше ветвлений.

    Слово counterexample в проекте используется осторожно:
    найденная трудная формула НЕ является математическим опровержением
    гипотезы. Это только стресс-тест, который показывает слабое место
    текущего алгоритма.
    """

    clauses = max(
        1,
        int(variables * ratio),
    )

    hardest = None

    for offset in range(tries):
        seed = seed_start + offset

        problem = random_3sat(
            variables=variables,
            clauses=clauses,
            seed=seed,
        )

        result = DPLLSolver().solve(problem)

        case = HardCase(
            seed=seed,
            variables=variables,
            clauses=clauses,
            sat=result.sat,
            decisions=result.decisions,
            calls=result.calls,
            seconds=result.seconds,
        )

        if hardest is None:
            hardest = case
        elif case.decisions > hardest.decisions:
            hardest = case

    return hardest
