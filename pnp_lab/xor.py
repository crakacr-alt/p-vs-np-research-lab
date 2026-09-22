from dataclasses import dataclass
from itertools import product

from .cnf import CNFProblem


@dataclass(frozen=True)
class XOREquation:
    """Уравнение XOR над GF(2).

    Пример:
        x1 XOR x2 XOR x3 = 1
    """

    variables: tuple[int, ...]
    rhs: bool


def _forbidden_assignment(clause: tuple[int, ...], variables: tuple[int, ...]):
    """Возвращает единственное присваивание, на котором клауза ложна."""

    literal_by_variable = {
        abs(literal): literal
        for literal in clause
    }

    assignment = []

    for variable in variables:
        literal = literal_by_variable[variable]

        # x ложно при x=0, а НЕ x ложно при x=1.
        assignment.append(0 if literal > 0 else 1)

    return tuple(assignment)


def detect_xor3(problem: CNFProblem):
    """Распознаёт точные 3-variable XOR-блоки в CNF.

    XOR из трёх переменных кодируется четырьмя 3-CNF клаузами.
    Мы преобразуем блок только если совпадение полное и однозначное.

    Возвращает:
        remaining_problem, equations
    """

    groups: dict[tuple[int, ...], list[tuple[int, tuple[int, ...]]]] = {}

    for index, clause in enumerate(problem.clauses):
        if len(clause) != 3:
            continue

        variables = tuple(sorted(abs(literal) for literal in clause))

        if len(set(variables)) != 3:
            continue

        groups.setdefault(variables, []).append((index, clause))

    used_indexes = set()
    equations = []

    for variables, items in groups.items():
        if len(items) != 4:
            continue

        forbidden = {
            _forbidden_assignment(clause, variables)
            for _, clause in items
        }

        if len(forbidden) != 4:
            continue

        parities = {
            sum(bits) % 2
            for bits in forbidden
        }

        if len(parities) != 1:
            continue

        forbidden_parity = next(iter(parities))
        allowed_rhs = bool(1 - forbidden_parity)

        equations.append(
            XOREquation(
                variables=variables,
                rhs=allowed_rhs,
            )
        )

        used_indexes.update(index for index, _ in items)

    remaining = tuple(
        clause
        for index, clause in enumerate(problem.clauses)
        if index not in used_indexes
    )

    return (
        CNFProblem(
            variables=problem.variables,
            clauses=remaining,
        ),
        tuple(equations),
    )


def xor3_to_cnf(equation: XOREquation):
    """Кодирует 3-variable XOR обратно в четыре CNF-клаузы.

    Функция нужна для benchmark-генераторов и тестов эквивалентности.
    """

    if len(equation.variables) != 3:
        raise ValueError("xor3_to_cnf поддерживает ровно три переменные")

    clauses = []

    for assignment in product([0, 1], repeat=3):
        parity = sum(assignment) % 2

        if parity == int(equation.rhs):
            continue

        clause = []

        for variable, value in zip(equation.variables, assignment):
            # Делаем клаузу ложной ровно на этом запрещённом присваивании.
            clause.append(variable if value == 0 else -variable)

        clauses.append(tuple(clause))

    return tuple(clauses)


def reduce_xor_system(
    equations: tuple[XOREquation, ...] | list[XOREquation],
    model: dict[int, bool],
):
    """Подставляет model и выполняет Gaussian elimination над GF(2).

    Возвращает:
        (reduced_equations, contradiction)
    """

    rows = []

    for equation in equations:
        variables = set(equation.variables)
        rhs = int(equation.rhs)

        for variable in list(variables):
            if variable in model:
                rhs ^= int(model[variable])
                variables.remove(variable)

        if not variables:
            if rhs:
                return (), True
            continue

        rows.append((variables, rhs))

    pivots: dict[int, tuple[set[int], int]] = {}

    for variables, rhs in rows:
        variables = set(variables)

        while variables:
            pivot = min(variables)

            if pivot not in pivots:
                pivots[pivot] = (variables, rhs)
                break

            pivot_variables, pivot_rhs = pivots[pivot]
            variables ^= pivot_variables
            rhs ^= pivot_rhs

        if not variables and rhs:
            return (), True

    # Backward elimination делает результат стабильнее и чаще создаёт unit equations.
    pivot_ids = sorted(pivots, reverse=True)

    for pivot in pivot_ids:
        pivot_variables, pivot_rhs = pivots[pivot]

        for other_pivot in sorted(pivots):
            if other_pivot >= pivot:
                continue

            other_variables, other_rhs = pivots[other_pivot]

            if pivot in other_variables:
                pivots[other_pivot] = (
                    other_variables ^ pivot_variables,
                    other_rhs ^ pivot_rhs,
                )

    reduced = []

    for pivot in sorted(pivots):
        variables, rhs = pivots[pivot]

        if not variables:
            if rhs:
                return (), True
            continue

        reduced.append(
            XOREquation(
                variables=tuple(sorted(variables)),
                rhs=bool(rhs),
            )
        )

    return tuple(reduced), False


def find_xor_unit(equations: tuple[XOREquation, ...]):
    """Ищет XOR-уравнение, где осталась одна переменная."""

    for equation in equations:
        if len(equation.variables) == 1:
            return equation.variables[0], equation.rhs

    return None


def solve_xor_system(
    equations: tuple[XOREquation, ...],
    model: dict[int, bool],
):
    """Достраивает model до решения XOR-системы.

    Свободные переменные ставятся в False. После Gaussian elimination это
    даёт одно из возможных решений системы.
    """

    reduced, contradiction = reduce_xor_system(equations, model)

    if contradiction:
        return None

    result = model.copy()

    pivot_variables = {
        equation.variables[0]
        for equation in reduced
    }

    all_variables = {
        variable
        for equation in reduced
        for variable in equation.variables
    }

    free_variables = all_variables - pivot_variables

    for variable in free_variables:
        result.setdefault(variable, False)

    for equation in reversed(reduced):
        pivot = equation.variables[0]
        value = int(equation.rhs)

        for variable in equation.variables[1:]:
            value ^= int(result.get(variable, False))

        result[pivot] = bool(value)

    return result


def canonical_xor(equations: tuple[XOREquation, ...]):
    """Стабильный ключ XOR-системы для memoization."""

    return tuple(
        sorted(
            (
                tuple(sorted(equation.variables)),
                bool(equation.rhs),
            )
            for equation in equations
        )
    )
