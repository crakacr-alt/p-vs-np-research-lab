import random

from .cnf import CNFProblem


def random_3sat(variables: int, clauses: int, seed: int | None = None) -> CNFProblem:
    """Создаёт воспроизводимую случайную 3-SAT задачу."""

    if variables < 3:
        raise ValueError("Для 3-SAT нужно минимум 3 переменные")

    if clauses < 0:
        raise ValueError("Количество клауз не может быть отрицательным")

    rng = random.Random(seed)
    result = []

    for _ in range(clauses):
        chosen = rng.sample(range(1, variables + 1), 3)
        clause = []

        for variable in chosen:
            clause.append(variable if rng.choice([True, False]) else -variable)

        result.append(tuple(clause))

    return CNFProblem(
        variables=variables,
        clauses=tuple(result),
    )


def planted_3sat(variables: int, clauses: int, seed: int | None = None):
    """Создаёт 3-SAT с заранее известным удовлетворяющим присваиванием."""

    if variables < 3:
        raise ValueError("Для 3-SAT нужно минимум 3 переменные")

    rng = random.Random(seed)
    planted_model = {
        variable: rng.choice([True, False])
        for variable in range(1, variables + 1)
    }

    result = []

    for _ in range(clauses):
        chosen = rng.sample(range(1, variables + 1), 3)

        while True:
            clause = []
            clause_true = False

            for variable in chosen:
                positive = rng.choice([True, False])
                literal = variable if positive else -variable
                clause.append(literal)

                value = planted_model[variable]
                literal_true = value if positive else not value
                clause_true = clause_true or literal_true

            if clause_true:
                break

        result.append(tuple(clause))

    return (
        CNFProblem(variables=variables, clauses=tuple(result)),
        planted_model,
    )
