from time import perf_counter

from .canonical import canonical_formula
from .cnf import CNFProblem, model_satisfies
from .decomposition import split_into_independent_components
from .heuristics import choose_jw_branch
from .metrics import SolveResult, SolverMetrics
from .xor import (
    canonical_xor,
    detect_xor3,
    find_xor_unit,
    reduce_xor_system,
    solve_xor_system,
)


class RepresentationSwitchingSolver:
    """Первый реальный прототип representation switching.

    Сейчас реализован один точный переход:

        CNF-блок из 4 клауз
        -> распознанное XOR-уравнение
        -> Gaussian elimination над GF(2)

    Остальная часть формулы остаётся CNF и решается точным DPLL-поиском.

    Важно: переход выполняется только при полном точном совпадении шаблона.
    """

    name = "representation-switch-v1.1"

    def __init__(self):
        self.metrics = SolverMetrics()
        self.unsat_cache: set[tuple] = set()

    def solve(self, problem: CNFProblem) -> SolveResult:
        self.metrics = SolverMetrics()
        self.unsat_cache = set()
        start = perf_counter()

        remaining_problem, equations = detect_xor3(problem)

        self.metrics.xor_equations_detected = len(equations)

        if equations:
            self.metrics.representation_switches = 1

        model = self._search(
            [list(clause) for clause in remaining_problem.clauses],
            equations,
            {},
            depth=0,
        )

        self.metrics.seconds = perf_counter() - start
        sat = model is not None
        final_model = model or {}

        if sat and not model_satisfies(problem, final_model):
            raise RuntimeError(
                "RepresentationSwitchingSolver нашёл модель, "
                "которая не прошла независимую проверку"
            )

        return SolveResult(
            sat=sat,
            model=final_model,
            solver=self.name,
            metrics=self.metrics,
        )

    def _search(self, clauses, equations, model, depth):
        self.metrics.calls += 1
        self.metrics.max_depth = max(self.metrics.max_depth, depth)

        simplified = self._simplify_cnf(clauses, model)

        if simplified is None:
            return None

        reduced_xor, xor_contradiction = reduce_xor_system(equations, model)

        if xor_contradiction:
            return None

        if not simplified:
            if not reduced_xor:
                return model

            self.metrics.xor_direct_solves += 1
            return solve_xor_system(reduced_xor, model)

        key = (
            canonical_formula(simplified),
            canonical_xor(reduced_xor),
        )

        if key in self.unsat_cache:
            self.metrics.cache_hits += 1
            return None

        unit_literal = self._find_unit_literal(simplified)

        if unit_literal is not None:
            self.metrics.unit_propagations += 1
            new_model = model.copy()
            new_model[abs(unit_literal)] = unit_literal > 0

            result = self._search(
                simplified,
                reduced_xor,
                new_model,
                depth + 1,
            )

            if result is None:
                self.unsat_cache.add(key)

            return result

        xor_unit = find_xor_unit(reduced_xor)

        if xor_unit is not None:
            variable, value = xor_unit
            self.metrics.xor_propagations += 1
            new_model = model.copy()
            new_model[variable] = value

            result = self._search(
                simplified,
                reduced_xor,
                new_model,
                depth + 1,
            )

            if result is None:
                self.unsat_cache.add(key)

            return result

        pure_assignment = self._find_safe_pure_literal(
            simplified,
            reduced_xor,
        )

        if pure_assignment is not None:
            variable, value = pure_assignment
            self.metrics.pure_literal_assignments += 1
            new_model = model.copy()
            new_model[variable] = value

            result = self._search(
                simplified,
                reduced_xor,
                new_model,
                depth + 1,
            )

            if result is None:
                self.unsat_cache.add(key)

            return result

        # Пока XOR-ограничения активны, не делим CNF отдельно:
        # XOR может связывать переменные из разных CNF-компонент.
        if not reduced_xor:
            components = split_into_independent_components(simplified)

            if len(components) > 1:
                self.metrics.decompositions += 1
                self.metrics.components_solved += len(components)
                combined_model = model.copy()

                for component in components:
                    result = self._search(
                        component,
                        (),
                        combined_model,
                        depth + 1,
                    )

                    if result is None:
                        self.unsat_cache.add(key)
                        return None

                    combined_model.update(result)

                return combined_model

        variable, preferred_value = choose_jw_branch(
            simplified,
            [equation.variables for equation in reduced_xor],
        )
        self.metrics.decisions += 1

        for value in (preferred_value, not preferred_value):
            new_model = model.copy()
            new_model[variable] = value

            result = self._search(
                simplified,
                reduced_xor,
                new_model,
                depth + 1,
            )

            if result is not None:
                return result

        self.unsat_cache.add(key)
        return None

    def _simplify_cnf(self, clauses, model):
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

    def _find_safe_pure_literal(self, clauses, equations):
        xor_variables = {
            variable
            for equation in equations
            for variable in equation.variables
        }

        signs: dict[int, set[bool]] = {}

        for clause in clauses:
            for literal in clause:
                variable = abs(literal)

                if variable in xor_variables:
                    continue

                signs.setdefault(variable, set()).add(literal > 0)

        for variable, values in signs.items():
            if len(values) == 1:
                return variable, next(iter(values))

        return None

