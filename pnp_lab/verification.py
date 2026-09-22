from dataclasses import dataclass

from .bruteforce import solve_bruteforce
from .dpll import DPLLSolver
from .generator import random_3sat
from .hybrid import HybridSolver
from .switch_solver import RepresentationSwitchingSolver


@dataclass
class VerificationSummary:
    checked: int
    baseline_vs_hybrid_mismatches: int
    switch_mismatches: int
    bruteforce_mismatches: int
    reference_mismatches: int


def cross_check_random(
    variables: int,
    clauses: int,
    count: int = 100,
    seed: int = 1,
    use_bruteforce: bool = False,
    use_reference: bool = False,
):
    """Сравнивает независимые реализации на одинаковых случайных задачах."""

    baseline_mismatches = 0
    switch_mismatches = 0
    bruteforce_mismatches = 0
    reference_mismatches = 0

    for index in range(count):
        current_seed = seed + index
        problem = random_3sat(variables, clauses, seed=current_seed)

        baseline = DPLLSolver().solve(problem)
        hybrid = HybridSolver().solve(problem)
        switching = RepresentationSwitchingSolver().solve(problem)

        if baseline.sat != hybrid.sat:
            baseline_mismatches += 1
            raise AssertionError(
                "DPLL и Hybrid дали разные ответы "
                f"на seed={current_seed}: {baseline.sat} != {hybrid.sat}"
            )

        if baseline.sat != switching.sat:
            switch_mismatches += 1
            raise AssertionError(
                "DPLL и RepresentationSwitchingSolver дали разные ответы "
                f"на seed={current_seed}: {baseline.sat} != {switching.sat}"
            )

        if use_bruteforce:
            brute_sat, _ = solve_bruteforce(problem)

            if baseline.sat != brute_sat:
                bruteforce_mismatches += 1
                raise AssertionError(
                    "DPLL и brute force дали разные ответы "
                    f"на seed={current_seed}: {baseline.sat} != {brute_sat}"
                )

        if use_reference:
            from .reference_solver import solve_with_pysat

            reference_sat, _ = solve_with_pysat(problem)

            if baseline.sat != reference_sat:
                reference_mismatches += 1
                raise AssertionError(
                    "Наши solver-ы и PySAT дали разные ответы "
                    f"на seed={current_seed}: {baseline.sat} != {reference_sat}"
                )

    return VerificationSummary(
        checked=count,
        baseline_vs_hybrid_mismatches=baseline_mismatches,
        switch_mismatches=switch_mismatches,
        bruteforce_mismatches=bruteforce_mismatches,
        reference_mismatches=reference_mismatches,
    )
