import random
from dataclasses import dataclass

from .cnf import CNFProblem
from .generator import random_3sat
from .hybrid import HybridSolver


@dataclass
class HardCase:
    problem: CNFProblem
    seed: int
    decisions: int
    calls: int
    seconds: float
    sat: bool


def _score(problem: CNFProblem):
    result = HybridSolver().solve(problem)
    return result.metrics.decisions, result


def mutate_3sat(problem: CNFProblem, rng: random.Random) -> CNFProblem:
    """Немного изменяет одну 3-SAT формулу."""

    clauses = [list(clause) for clause in problem.clauses]

    if not clauses:
        return problem

    clause_index = rng.randrange(len(clauses))
    clause = clauses[clause_index]

    if rng.choice([True, False]):
        literal_index = rng.randrange(len(clause))
        clause[literal_index] *= -1
    else:
        literal_index = rng.randrange(len(clause))
        used = {abs(value) for i, value in enumerate(clause) if i != literal_index}
        choices = [
            variable
            for variable in range(1, problem.variables + 1)
            if variable not in used
        ]

        new_variable = rng.choice(choices)
        sign = 1 if clause[literal_index] > 0 else -1
        clause[literal_index] = sign * new_variable

    clauses[clause_index] = clause

    return CNFProblem(
        variables=problem.variables,
        clauses=tuple(tuple(item) for item in clauses),
    )


def search_hard_case(
    variables: int,
    clauses: int,
    iterations: int = 100,
    seed: int = 1,
):
    """Ищет трудный экземпляр для HybridSolver простым hill climbing.

    Это не поиск математического контрпримера P vs NP.
    """

    rng = random.Random(seed)
    current = random_3sat(variables, clauses, seed=seed)
    current_score, current_result = _score(current)

    best = HardCase(
        problem=current,
        seed=seed,
        decisions=current_result.metrics.decisions,
        calls=current_result.metrics.calls,
        seconds=current_result.metrics.seconds,
        sat=current_result.sat,
    )

    for _ in range(iterations):
        candidate = mutate_3sat(current, rng)
        candidate_score, candidate_result = _score(candidate)

        if candidate_score >= current_score:
            current = candidate
            current_score = candidate_score

        if candidate_score > best.decisions:
            best = HardCase(
                problem=candidate,
                seed=seed,
                decisions=candidate_result.metrics.decisions,
                calls=candidate_result.metrics.calls,
                seconds=candidate_result.metrics.seconds,
                sat=candidate_result.sat,
            )

    return best
