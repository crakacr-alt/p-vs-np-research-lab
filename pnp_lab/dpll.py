from time import perf_counter

from .cnf import CNFProblem, model_satisfies
from .metrics import SolveResult, SolverMetrics


class DPLLSolver:
    """Понятный baseline solver на основе DPLL.

    Baseline нужен не потому, что он самый быстрый, а потому что с ним удобно
    честно сравнивать будущие улучшения.
    """

    name = "dpll-baseline"

    def __init__(self):
        self.metrics = SolverMetrics()

    def solve(self, problem: CNFProblem) -> SolveResult:
        self.metrics = SolverMetrics()
        start = perf_counter()

        model = self._search(
            [list(clause) for clause in problem.clauses],
            {},
            depth=0,
        )

        self.metrics.seconds = perf_counter() - start
        sat = model is not None
        final_model = model or {}

        if sat and not model_satisfies(problem, final_model):
            raise RuntimeError("DPLL нашёл модель, которая не прошла независимую проверку")

        return SolveResult(
            sat=sat,
            model=final_model,
            solver=self.name,
            metrics=self.metrics,
        )

    def _search(self, clauses: list[list[int]], model: dict[int, bool], depth: int):
        self.metrics.calls += 1
        self.metrics.max_depth = max(self.metrics.max_depth, depth)

        simplified = self._simplify_all(clauses, model)

        if simplified is None:
            return None

        if not simplified:
            return model

        unit_literal = self._find_unit_literal(simplified)

        if unit_literal is not None:
            self.metrics.unit_propagations += 1
            new_model = model.copy()
            new_model[abs(unit_literal)] = unit_literal > 0
            return self._search(simplified, new_model, depth + 1)

        variable = self._choose_variable(simplified)
        self.metrics.decisions += 1

        for value in (True, False):
            new_model = model.copy()
            new_model[variable] = value
            result = self._search(simplified, new_model, depth + 1)

            if result is not None:
                return result

        return None

    def _simplify_all(self, clauses, model):
        result = []

        for clause in clauses:
            new_clause = []
            clause_is_true = False

            for literal in clause:
                variable = abs(literal)

                if variable not in model:
                    new_clause.append(literal)
                    continue

                value = model[variable]
                literal_is_true = value if literal > 0 else not value

                if literal_is_true:
                    clause_is_true = True
                    break

            if clause_is_true:
                continue

            if not new_clause:
                return None

            result.append(new_clause)

        return result

    def _find_unit_literal(self, clauses):
        for clause in clauses:
            if len(clause) == 1:
                return clause[0]

        return None

    def _choose_variable(self, clauses):
        counts = {}

        for clause in clauses:
            for literal in clause:
                variable = abs(literal)
                counts[variable] = counts.get(variable, 0) + 1

        return max(counts, key=counts.get)
