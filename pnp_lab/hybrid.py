from time import perf_counter

from .canonical import canonical_formula
from .cnf import CNFProblem, model_satisfies
from .decomposition import split_into_independent_components
from .metrics import SolveResult, SolverMetrics


class HybridSolver:
    """Точный гибридный SAT solver для исследовательских экспериментов.

    Он использует несколько безопасных приёмов:
    - unit propagation;
    - pure literal elimination;
    - разбиение на независимые компоненты;
    - memoization для уже доказанных UNSAT-состояний;
    - обычное DPLL-ветвление, если упрощения закончились.

    Ни один из этих шагов не является вероятностным угадыванием ответа.
    """

    name = "hybrid-exact-v0.2"

    def __init__(self):
        self.metrics = SolverMetrics()
        self.unsat_cache: set[tuple] = set()

    def solve(self, problem: CNFProblem) -> SolveResult:
        self.metrics = SolverMetrics()
        self.unsat_cache = set()
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
            raise RuntimeError("Hybrid solver нашёл модель, которая не прошла проверку")

        return SolveResult(
            sat=sat,
            model=final_model,
            solver=self.name,
            metrics=self.metrics,
        )

    def _search(self, clauses, model, depth):
        self.metrics.calls += 1
        self.metrics.max_depth = max(self.metrics.max_depth, depth)

        simplified = self._simplify(clauses, model)

        if simplified is None:
            return None

        if not simplified:
            return model

        key = canonical_formula(simplified)

        if key in self.unsat_cache:
            self.metrics.cache_hits += 1
            return None

        unit_literal = self._find_unit_literal(simplified)

        if unit_literal is not None:
            self.metrics.unit_propagations += 1
            new_model = model.copy()
            new_model[abs(unit_literal)] = unit_literal > 0
            result = self._search(simplified, new_model, depth + 1)

            if result is None:
                self.unsat_cache.add(key)

            return result

        pure_assignment = self._find_pure_literal(simplified)

        if pure_assignment is not None:
            variable, value = pure_assignment
            self.metrics.pure_literal_assignments += 1
            new_model = model.copy()
            new_model[variable] = value
            result = self._search(simplified, new_model, depth + 1)

            if result is None:
                self.unsat_cache.add(key)

            return result

        components = split_into_independent_components(simplified)

        if len(components) > 1:
            self.metrics.decompositions += 1
            combined_model = model.copy()

            for component in components:
                result = self._search(component, combined_model, depth + 1)

                if result is None:
                    self.unsat_cache.add(key)
                    return None

                combined_model.update(result)

            return combined_model

        variable = self._choose_variable(simplified)
        self.metrics.decisions += 1

        for value in (True, False):
            new_model = model.copy()
            new_model[variable] = value
            result = self._search(simplified, new_model, depth + 1)

            if result is not None:
                return result

        self.unsat_cache.add(key)
        return None

    def _simplify(self, clauses, model):
        result = []

        for clause in clauses:
            new_clause = []
            clause_true = False

            for literal in clause:
                variable = abs(literal)

                if variable not in model:
                    new_clause.append(literal)
                    continue

                value = model[variable]
                literal_true = value if literal > 0 else not value

                if literal_true:
                    clause_true = True
                    break

            if clause_true:
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

    def _find_pure_literal(self, clauses):
        """Ищет переменную, встречающуюся только с одним знаком."""

        signs: dict[int, set[bool]] = {}

        for clause in clauses:
            for literal in clause:
                variable = abs(literal)
                signs.setdefault(variable, set()).add(literal > 0)

        for variable, values in signs.items():
            if len(values) == 1:
                return variable, next(iter(values))

        return None

    def _choose_variable(self, clauses):
        counts = {}

        for clause in clauses:
            for literal in clause:
                variable = abs(literal)
                counts[variable] = counts.get(variable, 0) + 1

        return max(counts, key=counts.get)
