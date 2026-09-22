from dataclasses import dataclass
from time import perf_counter

from .cnf import model_satisfies


@dataclass
class SolveResult:
    """Результат работы solver-а."""

    sat: bool
    model: dict
    decisions: int
    calls: int
    seconds: float


class DPLLSolver:
    """Простой точный SAT solver на основе DPLL.

    Почему начинаем именно с DPLL:
    1. алгоритм сравнительно легко понять;
    2. он точный;
    3. на его фоне удобно измерять будущие улучшения.

    Это не промышленный solver. Это понятная контрольная точка
    (baseline) для исследовательских экспериментов.
    """

    def __init__(self):
        self.decisions = 0
        self.calls = 0

    def solve(self, problem):
        """Решает задачу и возвращает SAT или UNSAT."""

        # Счётчики каждый запуск начинаются с нуля.
        self.decisions = 0
        self.calls = 0

        start = perf_counter()

        model = self._search(
            problem.clauses,
            {},
        )

        elapsed = perf_counter() - start
        sat = model is not None

        # Очень важная страховка:
        # найденный SAT-ответ проверяется второй функцией.
        if sat and not model_satisfies(problem, model):
            raise RuntimeError(
                "Внутренняя ошибка: найденная модель не прошла проверку"
            )

        return SolveResult(
            sat=sat,
            model=model or {},
            decisions=self.decisions,
            calls=self.calls,
            seconds=elapsed,
        )

    def _search(self, clauses, model):
        """Рекурсивная часть DPLL."""

        self.calls += 1

        # Подставляем все уже известные значения.
        simplified = self._simplify_all(
            clauses,
            model,
        )

        # None означает противоречие.
        if simplified is None:
            return None

        # Если клауз больше нет, все они выполнены.
        if not simplified:
            return model

        # Unit propagation:
        # если клауза состоит из одного литерала,
        # нужное значение переменной уже однозначно.
        unit_literal = self._find_unit_literal(
            simplified
        )

        if unit_literal is not None:
            new_model = model.copy()
            new_model[abs(unit_literal)] = unit_literal > 0

            return self._search(
                simplified,
                new_model,
            )

        # Если вынужденного значения нет,
        # нужно сделать настоящее ветвление.
        variable = self._choose_variable(
            simplified
        )

        self.decisions += 1

        # Пробуем обе возможные ветви.
        for value in (True, False):
            new_model = model.copy()
            new_model[variable] = value

            result = self._search(
                simplified,
                new_model,
            )

            if result is not None:
                return result

        # Обе ветви закончились противоречием.
        return None

    def _simplify_all(self, clauses, model):
        """Подставляет значения model во все клаузы."""

        result = []

        for clause in clauses:
            new_clause = []
            clause_is_true = False

            for literal in clause:
                variable = abs(literal)

                # Переменная пока неизвестна.
                if variable not in model:
                    new_clause.append(literal)
                    continue

                value = model[variable]

                if literal > 0:
                    literal_is_true = value
                else:
                    literal_is_true = not value

                # Если хотя бы один литерал истинен,
                # вся клауза уже выполнена.
                if literal_is_true:
                    clause_is_true = True
                    break

            if clause_is_true:
                continue

            # Пустая невыполненная клауза = противоречие.
            if not new_clause:
                return None

            result.append(new_clause)

        return result

    def _find_unit_literal(self, clauses):
        """Ищет клаузу, где остался только один литерал."""

        for clause in clauses:
            if len(clause) == 1:
                return clause[0]

        return None

    def _choose_variable(self, clauses):
        """Выбирает переменную для ветвления.

        Простая эвристика:
        чаще встречающаяся переменная влияет на большее число клауз.
        """

        counts = {}

        for clause in clauses:
            for literal in clause:
                variable = abs(literal)

                counts[variable] = (
                    counts.get(variable, 0) + 1
                )

        return max(
            counts,
            key=counts.get,
        )
