import csv
import json
import platform
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .complexity import fit_exponential, fit_polynomial
from .dpll import DPLLSolver
from .generator import random_3sat
from .hybrid import HybridSolver
from .switch_solver import RepresentationSwitchingSolver


@dataclass
class ExperimentRow:
    variables: int
    clauses: int
    repeat: int
    seed: int
    solver: str
    sat: bool
    decisions: int
    calls: int
    unit_propagations: int
    pure_literal_assignments: int
    cache_hits: int
    decompositions: int
    max_depth: int
    xor_equations_detected: int
    xor_propagations: int
    xor_direct_solves: int
    representation_switches: int
    seconds: float


def _make_solver(name):
    if name == "dpll":
        return DPLLSolver()

    if name == "hybrid":
        return HybridSolver()

    if name == "switch":
        return RepresentationSwitchingSolver()

    raise ValueError("Неизвестный solver. Используйте: dpll, hybrid или switch")


def run_growth_experiment(
    start: int,
    stop: int,
    step: int,
    repeats: int = 5,
    ratio: float = 4.2,
    seed: int = 1,
    solvers=("dpll", "hybrid", "switch"),
):
    """Запускает воспроизводимый сравнительный эксперимент."""

    rows = []

    for variables in range(start, stop + 1, step):
        clauses = max(1, int(variables * ratio))

        for repeat in range(repeats):
            current_seed = seed + variables * 100_000 + repeat
            problem = random_3sat(variables, clauses, seed=current_seed)

            for solver_name in solvers:
                result = _make_solver(solver_name).solve(problem)
                metrics = result.metrics

                rows.append(
                    ExperimentRow(
                        variables=variables,
                        clauses=clauses,
                        repeat=repeat,
                        seed=current_seed,
                        solver=result.solver,
                        sat=result.sat,
                        decisions=metrics.decisions,
                        calls=metrics.calls,
                        unit_propagations=metrics.unit_propagations,
                        pure_literal_assignments=metrics.pure_literal_assignments,
                        cache_hits=metrics.cache_hits,
                        decompositions=metrics.decompositions,
                        max_depth=metrics.max_depth,
                        xor_equations_detected=metrics.xor_equations_detected,
                        xor_propagations=metrics.xor_propagations,
                        xor_direct_solves=metrics.xor_direct_solves,
                        representation_switches=metrics.representation_switches,
                        seconds=metrics.seconds,
                    )
                )

    return rows


def summarize_growth(rows, solver_name, cost_field="calls"):
    """Строит простую эмпирическую оценку роста.

    Это НЕ доказательство асимптотики.
    """

    grouped = {}

    for row in rows:
        if row.solver != solver_name:
            continue

        grouped.setdefault(row.variables, []).append(getattr(row, cost_field))

    ns = sorted(grouped)
    averages = [sum(grouped[n]) / len(grouped[n]) for n in ns]

    if len(ns) < 2:
        return None

    polynomial = fit_polynomial(ns, averages)
    exponential = fit_exponential(ns, averages)

    return {
        "solver": solver_name,
        "cost_field": cost_field,
        "n": ns,
        "average_cost": averages,
        "polynomial_fit": asdict(polynomial),
        "exponential_fit": asdict(exponential),
        "warning": (
            "Это эмпирическая подгонка по конечным данным. "
            "Она не доказывает polynomial или exponential worst-case complexity."
        ),
    }


def save_experiment(rows, output_dir, metadata=None):
    """Сохраняет сырые данные в CSV и метаданные в JSON."""

    if not rows:
        raise ValueError("Нельзя сохранить пустой эксперимент")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "results.csv"
    json_path = output_dir / "metadata.json"

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()

        for row in rows:
            writer.writerow(asdict(row))

    document = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": len(rows),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "metadata": metadata or {},
    }

    json_path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return csv_path, json_path
