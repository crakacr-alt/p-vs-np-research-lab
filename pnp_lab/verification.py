from dataclasses import dataclass

from .dpll import DPLLSolver
from .generator import random_3sat
from .hybrid import HybridSolver


@dataclass
class VerificationSummary:
    checked: int
    baseline_vs_hybrid_mismatches: int
    reference_mismatches: int


def cross_check_random(
    variables: int,
    clauses: int,
    count: int = 100,
    seed: int = 1,
    use_reference: bool = False,
):
    """Сравнивает независимые реализации на одинаковых случайных задачах."""

    baseline_mismatches = 0
    reference_mismatches = 0

    for index in range(count):
        current_seed = seed + index
        problem = random_3sat(variables, clauses, seed=current_seed)

        baseline = DPLLSolver().solve(problem)
        hybrid = HybridSolver().solve(problem)

        if baseline.sat != hybrid.sat:
            baseline_mismatches += 1
            raise AssertionError(
                "DPLL и Hybrid дали разные ответы "
                f"на seed={current_seed}: {baseline.sat} != {hybrid.sat}"
            )

        if use_reference:
            from .reference_solver import solve_with_pysat

            reference_sat, _ = solve_with_pysat(problem)

            if hybrid.sat != reference_sat:
                reference_mismatches += 1
                raise AssertionError(
                    "Hybrid и PySAT дали разные ответы "
                    f"на seed={current_seed}: {hybrid.sat} != {reference_sat}"
                )

    return VerificationSummary(
        checked=count,
        baseline_vs_hybrid_mismatches=baseline_mismatches,
        reference_mismatches=reference_mismatches,
    )
