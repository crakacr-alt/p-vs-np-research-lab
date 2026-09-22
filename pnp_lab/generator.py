import random

from .cnf import CNFProblem


def random_3sat(variables, clauses, seed=None):
    """Создаёт случайную 3-SAT задачу.

    seed нужен для воспроизводимости:
    один и тот же seed создаёт одну и ту же формулу.
    """

    if variables < 3:
        raise ValueError(
            "Для 3-SAT нужно минимум 3 переменные"
        )

    rng = random.Random(seed)
    result = []

    for _ in range(clauses):
        # В одной 3-SAT клаузе берём три разные переменные.
        chosen = rng.sample(
            range(1, variables + 1),
            3,
        )

        clause = []

        for variable in chosen:
            positive = rng.choice(
                [True, False]
            )

            if positive:
                clause.append(variable)
            else:
                clause.append(-variable)

        result.append(clause)

    return CNFProblem(
        variables=variables,
        clauses=result,
    )
