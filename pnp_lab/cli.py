import argparse
import json
from pathlib import Path

from .cnf import load_dimacs, save_dimacs
from .dpll import DPLLSolver
from .experiments import run_growth_experiment, save_experiment, summarize_growth
from .hard_search import search_hard_case
from .hybrid import HybridSolver
from .research_db import ALLOWED_STATUSES, ResearchDatabase
from .verification import cross_check_random


def _solver(name):
    return DPLLSolver() if name == "dpll" else HybridSolver()


def solve_command(args):
    problem = load_dimacs(args.file)
    result = _solver(args.solver).solve(problem)

    print("SAT" if result.sat else "UNSAT")
    print(f"solver: {result.solver}")

    for key, value in result.metrics.to_dict().items():
        print(f"{key}: {value}")

    if result.sat:
        model = ", ".join(
            f"x{variable}={1 if value else 0}"
            for variable, value in sorted(result.model.items())
        )
        print("model:", model)


def experiment_command(args):
    rows = run_growth_experiment(
        start=args.start,
        stop=args.stop,
        step=args.step,
        repeats=args.repeats,
        ratio=args.ratio,
        seed=args.seed,
        solvers=tuple(args.solvers.split(",")),
    )

    output = Path(args.output)
    csv_path, metadata_path = save_experiment(
        rows,
        output,
        metadata={
            "start": args.start,
            "stop": args.stop,
            "step": args.step,
            "repeats": args.repeats,
            "ratio": args.ratio,
            "seed": args.seed,
            "solvers": args.solvers,
        },
    )

    print(f"CSV: {csv_path}")
    print(f"metadata: {metadata_path}")

    for solver_name in sorted({row.solver for row in rows}):
        summary = summarize_growth(rows, solver_name)

        if summary:
            print(json.dumps(summary, ensure_ascii=False, indent=2))


def hunt_command(args):
    case = search_hard_case(
        variables=args.variables,
        clauses=args.clauses,
        iterations=args.iterations,
        seed=args.seed,
    )

    save_dimacs(case.problem, args.output)

    print("Найден трудный стресс-тест")
    print(f"decisions: {case.decisions}")
    print(f"calls: {case.calls}")
    print(f"sat: {case.sat}")
    print(f"saved: {args.output}")
    print("Важно: это НЕ математический контрпример P vs NP.")


def verify_command(args):
    summary = cross_check_random(
        variables=args.variables,
        clauses=args.clauses,
        count=args.count,
        seed=args.seed,
        use_reference=args.reference,
    )

    print(f"Проверено задач: {summary.checked}")
    print(f"DPLL vs Hybrid mismatches: {summary.baseline_vs_hybrid_mismatches}")
    print(f"Reference mismatches: {summary.reference_mismatches}")
    print(
        "Несовпадений не найдено."
        if summary.baseline_vs_hybrid_mismatches == 0 and summary.reference_mismatches == 0
        else "Есть несовпадения."
    )


def hypothesis_add_command(args):
    database = ResearchDatabase(args.db)
    hypothesis_id = database.add_hypothesis(args.title, args.statement, args.notes)
    print(f"Добавлена гипотеза H{hypothesis_id:04d}")


def hypothesis_list_command(args):
    database = ResearchDatabase(args.db)

    for item in database.list_hypotheses():
        print(f"H{item.id:04d} [{item.status}] {item.title}")
        print(f"  {item.statement}")
        if item.notes:
            print(f"  notes: {item.notes}")


def hypothesis_status_command(args):
    database = ResearchDatabase(args.db)
    database.set_status(args.id, args.status, args.notes)
    print(f"Статус H{args.id:04d} -> {args.status}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="P vs NP Research Lab — воспроизводимые SAT-эксперименты"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    solve_parser = commands.add_parser("solve", help="решить DIMACS CNF")
    solve_parser.add_argument("file")
    solve_parser.add_argument("--solver", choices=["dpll", "hybrid"], default="hybrid")
    solve_parser.set_defaults(handler=solve_command)

    experiment_parser = commands.add_parser("experiment", help="серия экспериментов роста")
    experiment_parser.add_argument("--start", type=int, default=10)
    experiment_parser.add_argument("--stop", type=int, default=30)
    experiment_parser.add_argument("--step", type=int, default=5)
    experiment_parser.add_argument("--repeats", type=int, default=5)
    experiment_parser.add_argument("--ratio", type=float, default=4.2)
    experiment_parser.add_argument("--seed", type=int, default=1)
    experiment_parser.add_argument("--solvers", default="dpll,hybrid")
    experiment_parser.add_argument("--output", default="results/latest")
    experiment_parser.set_defaults(handler=experiment_command)

    hunt_parser = commands.add_parser("hunt", help="поиск трудного стресс-теста")
    hunt_parser.add_argument("--variables", type=int, default=20)
    hunt_parser.add_argument("--clauses", type=int, default=84)
    hunt_parser.add_argument("--iterations", type=int, default=100)
    hunt_parser.add_argument("--seed", type=int, default=1)
    hunt_parser.add_argument("--output", default="results/hard_case.cnf")
    hunt_parser.set_defaults(handler=hunt_command)

    verify_parser = commands.add_parser("verify", help="сверить независимые solver-ы")
    verify_parser.add_argument("--variables", type=int, default=10)
    verify_parser.add_argument("--clauses", type=int, default=42)
    verify_parser.add_argument("--count", type=int, default=100)
    verify_parser.add_argument("--seed", type=int, default=1)
    verify_parser.add_argument(
        "--reference",
        action="store_true",
        help="также сверять с optional PySAT",
    )
    verify_parser.set_defaults(handler=verify_command)

    hypothesis = commands.add_parser("hypothesis", help="журнал исследовательских гипотез")
    hypothesis_commands = hypothesis.add_subparsers(dest="hypothesis_command", required=True)

    add_parser = hypothesis_commands.add_parser("add")
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--statement", required=True)
    add_parser.add_argument("--notes", default="")
    add_parser.add_argument("--db", default="research/research.db")
    add_parser.set_defaults(handler=hypothesis_add_command)

    list_parser = hypothesis_commands.add_parser("list")
    list_parser.add_argument("--db", default="research/research.db")
    list_parser.set_defaults(handler=hypothesis_list_command)

    status_parser = hypothesis_commands.add_parser("status")
    status_parser.add_argument("id", type=int)
    status_parser.add_argument("status", choices=sorted(ALLOWED_STATUSES))
    status_parser.add_argument("--notes")
    status_parser.add_argument("--db", default="research/research.db")
    status_parser.set_defaults(handler=hypothesis_status_command)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
