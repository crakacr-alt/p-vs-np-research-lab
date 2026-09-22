from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CNFProblem:
    """SAT-задача в конъюнктивной нормальной форме (CNF).

    Литерал хранится целым числом:
    - 3 означает x3;
    - -3 означает НЕ x3.
    """

    variables: int
    clauses: tuple[tuple[int, ...], ...]

    def validate(self) -> None:
        """Проверяет базовую корректность задачи."""

        if self.variables < 0:
            raise ValueError("Количество переменных не может быть отрицательным")

        for clause in self.clauses:
            for literal in clause:
                if literal == 0:
                    raise ValueError("Ноль не хранится внутри объекта CNFProblem")

                if abs(literal) > self.variables:
                    raise ValueError(
                        f"Литерал {literal} ссылается на переменную вне диапазона 1..{self.variables}"
                    )


def load_dimacs(path: str | Path) -> CNFProblem:
    """Читает DIMACS CNF-файл с диска."""

    text = Path(path).read_text(encoding="utf-8")
    return parse_dimacs(text)


def parse_dimacs(text: str) -> CNFProblem:
    """Преобразует текст DIMACS в объект CNFProblem.

    Пример:
        p cnf 3 2
        1 -2 3 0
        -1 2 0
    """

    variables = None
    expected_clauses = None
    clauses: list[tuple[int, ...]] = []
    current_clause: list[int] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Комментарии DIMACS начинаются с c.
        if not line or line.startswith("c"):
            continue

        if line.startswith("p"):
            parts = line.split()

            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError("Неверный заголовок DIMACS. Ожидалось: p cnf N M")

            variables = int(parts[2])
            expected_clauses = int(parts[3])
            continue

        for token in line.split():
            literal = int(token)

            if literal == 0:
                clauses.append(tuple(current_clause))
                current_clause = []
            else:
                current_clause.append(literal)

    if variables is None:
        raise ValueError("В DIMACS отсутствует строка 'p cnf N M'")

    if current_clause:
        raise ValueError("Последняя клауза должна заканчиваться числом 0")

    if expected_clauses != len(clauses):
        raise ValueError(
            "Количество клауз не совпадает с заголовком DIMACS: "
            f"ожидалось {expected_clauses}, получено {len(clauses)}"
        )

    problem = CNFProblem(
        variables=variables,
        clauses=tuple(clauses),
    )
    problem.validate()
    return problem


def to_dimacs(problem: CNFProblem) -> str:
    """Преобразует CNFProblem обратно в DIMACS.

    Это полезно для сохранения трудных найденных экземпляров.
    """

    problem.validate()
    lines = [f"p cnf {problem.variables} {len(problem.clauses)}"]

    for clause in problem.clauses:
        literals = " ".join(str(value) for value in clause)
        lines.append(f"{literals} 0")

    return "\n".join(lines) + "\n"


def save_dimacs(problem: CNFProblem, path: str | Path) -> None:
    """Сохраняет задачу в DIMACS CNF."""

    Path(path).write_text(to_dimacs(problem), encoding="utf-8")


def model_satisfies(problem: CNFProblem, model: dict[int, bool]) -> bool:
    """Независимо проверяет SAT-модель.

    Важно: эта функция не использует внутреннюю логику solver-а.
    Она является дополнительной защитой от ошибок в алгоритме поиска.
    """

    for clause in problem.clauses:
        clause_is_true = False

        for literal in clause:
            value = model.get(abs(literal), False)

            if literal < 0:
                value = not value

            if value:
                clause_is_true = True
                break

        if not clause_is_true:
            return False

    return True
