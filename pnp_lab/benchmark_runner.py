import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .benchmarks import BenchmarkCase, release_suite
from .dpll import DPLLSolver
from .hybrid import HybridSolver
from .switch_solver import RepresentationSwitchingSolver


@dataclass
class BenchmarkResult:
    case: str
    family: str
    variables: int
    clauses: int
    expected_sat: bool | None
    solver: str
    sat: bool
    matches_expected: bool | None
    decisions: int
    calls: int
    cache_hits: int
    decompositions: int
    components_solved: int
    unit_propagations: int
    pure_literal_assignments: int
    max_depth: int
    xor_equations_detected: int
    xor_propagations: int
    xor_direct_solves: int
    representation_switches: int
    seconds: float


def make_solver(name: str):
    if name == "dpll":
        return DPLLSolver()

    if name == "hybrid":
        return HybridSolver()

    if name == "switch":
        return RepresentationSwitchingSolver()

    raise ValueError("Неизвестный solver. Используйте dpll, hybrid или switch")


def run_benchmark_cases(
    cases: list[BenchmarkCase],
    solvers=("dpll", "hybrid", "switch"),
):
    """Запускает все solver-ы на одинаковых benchmark-входах."""

    results = []

    for case in cases:
        answers = set()

        for solver_name in solvers:
            result = make_solver(solver_name).solve(case.problem)
            metrics = result.metrics
            answers.add(result.sat)

            if case.expected_sat is None:
                matches_expected = None
            else:
                matches_expected = result.sat == case.expected_sat

            results.append(
                BenchmarkResult(
                    case=case.name,
                    family=case.family,
                    variables=case.problem.variables,
                    clauses=len(case.problem.clauses),
                    expected_sat=case.expected_sat,
                    solver=result.solver,
                    sat=result.sat,
                    matches_expected=matches_expected,
                    decisions=metrics.decisions,
                    calls=metrics.calls,
                    cache_hits=metrics.cache_hits,
                    decompositions=metrics.decompositions,
                    components_solved=metrics.components_solved,
                    unit_propagations=metrics.unit_propagations,
                    pure_literal_assignments=metrics.pure_literal_assignments,
                    max_depth=metrics.max_depth,
                    xor_equations_detected=metrics.xor_equations_detected,
                    xor_propagations=metrics.xor_propagations,
                    xor_direct_solves=metrics.xor_direct_solves,
                    representation_switches=metrics.representation_switches,
                    seconds=metrics.seconds,
                )
            )

        if len(answers) != 1:
            raise AssertionError(
                f"Solver-ы дали разные SAT/UNSAT ответы на benchmark {case.name}"
            )

    return results


def run_release_suite(seed: int = 1):
    return run_benchmark_cases(release_suite(seed=seed))


def _format_optional(value):
    if value is None:
        return "—"
    return str(value)


def build_markdown_report(results: list[BenchmarkResult]):
    """Строит читаемый Markdown-отчёт без внешних библиотек."""

    lines = [
        "# Benchmark report",
        "",
        "> Это экспериментальные измерения, а не доказательство асимптотики.",
        "",
        "| Case | Family | Solver | SAT | Decisions | Calls | Components | Depth | XOR eq | Switches | Seconds |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in results:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.case,
                    row.family,
                    row.solver,
                    str(row.sat),
                    str(row.decisions),
                    str(row.calls),
                    str(row.components_solved),
                    str(row.max_depth),
                    str(row.xor_equations_detected),
                    str(row.representation_switches),
                    f"{row.seconds:.6f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Проверка ожидаемых ответов",
            "",
        ]
    )

    for row in results:
        lines.append(
            f"- {row.case} / {row.solver}: "
            f"expected={_format_optional(row.expected_sat)}, "
            f"observed={row.sat}, "
            f"match={_format_optional(row.matches_expected)}"
        )

    return "\n".join(lines) + "\n"


def save_benchmark(results, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "benchmark.csv"
    json_path = output_dir / "benchmark.json"
    report_path = output_dir / "REPORT.md"

    fields = list(asdict(results[0]).keys())

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for row in results:
            writer.writerow(asdict(row))

    json_path.write_text(
        json.dumps(
            {
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "results": [asdict(row) for row in results],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    report_path.write_text(
        build_markdown_report(results),
        encoding="utf-8",
    )

    return csv_path, json_path, report_path
