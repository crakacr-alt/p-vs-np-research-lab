from dataclasses import dataclass
from pathlib import Path


@dataclass
class CNFProblem:
    """Одна SAT-задача в формате CNF."""

    variables: int
    clauses: list[list[int]]


def load_dimacs(path):
    """Читает DIMACS CNF-файл с диска."""

    text = Path(path).read_text(encoding="utf-8")
    return parse_dimacs(text)


def parse_dimacs(text):
    """Преобразует текст DIMACS в объект CNFProblem.

    Пример строки:
        1 -2 3 0

    Она означает:
        x1 ИЛИ НЕ x2 ИЛИ x3

    Ноль обозначает конец клаузы.
    """

    variables = 0
    expected_clauses = None

    clauses = []
    current_clause = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Пустые строки и комментарии нам не нужны.
        if not line or line.startswith("c"):
            continue

        # Заголовок сообщает количество переменных и клауз.
        if line.startswith("p"):
            parts = line.split()

            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError(
                    "Неверный заголовок DIMACS. Ожидалось: p cnf N M"
                )

            variables = int(parts[2])
            expected_clauses = int(parts[3])
            continue

        # Обычная строка содержит литералы.
        for token in line.split():
            number = int(token)

            if number == 0:
                clauses.append(current_clause)
                current_clause = []
            else:
                current_clause.append(number)

    if current_clause:
        raise ValueError(
            "Последняя клауза должна заканчиваться числом 0"
        )

    if expected_clauses is not None:
        if expected_clauses != len(clauses):
            raise ValueError(
                "Количество клауз не совпадает с заголовком DIMACS"
            )

    return CNFProblem(
        variables=variables,
        clauses=clauses,
    )


def model_satisfies(problem, model):
    """Независимо проверяет найденное решение.

    Эта функция специально отделена от solver-а.
    Даже если в алгоритме поиска будет ошибка, итоговая модель
    должна пройти дополнительную проверку.
    """

    for clause in problem.clauses:
        clause_is_true = False

        for literal in clause:
            variable = abs(literal)
            value = model.get(variable, False)

            # Отрицательный литерал означает НЕ x.
            if literal < 0:
                value = not value

            if value:
                clause_is_true = True
                break

        # В CNF каждая клауза должна быть истинной.
        if not clause_is_true:
            return False

    return True
