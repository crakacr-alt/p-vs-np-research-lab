from dataclasses import dataclass

from .dpll import DPLLSolver
from .generator import random_3sat


@dataclass
class ExperimentRow:
    variables: int
    clauses: int
    sat: bool
    decisions: int
    calls: int
    seconds: float


def run_growth_experiment(
    start,
    stop,
    step,
    ratio=4.2,
    seed=1,
):
    """Смотрит, как меняется стоимость решения при росте n.

    ratio задаёт примерное отношение:
        количество клауз / количество переменных.

    Важно:
    красивый график или медленный рост НЕ доказывает P = NP.
    Это только экспериментальное наблюдение.
    """

    rows = []

    for variables in range(
        start,
        stop + 1,
        step,
    ):
        clauses = max(
            1,
            int(variables * ratio),
        )

        problem = random_3sat(
            variables=variables,
            clauses=clauses,
            seed=seed + variables,
        )

        result = DPLLSolver().solve(problem)

        row = ExperimentRow(
            variables=variables,
            clauses=clauses,
            sat=result.sat,
            decisions=result.decisions,
            calls=result.calls,
            seconds=result.seconds,
        )

        rows.append(row)

    return rows
