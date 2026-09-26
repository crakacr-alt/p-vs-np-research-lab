import argparse
import json
from pathlib import Path

from .benchmark_runner import run_release_suite, save_benchmark
from .cnf import load_dimacs, save_dimacs
from .doctor import run_doctor
from .dpll import DPLLSolver
from .experiments import run_growth_experiment, save_experiment, summarize_growth
from .hard_search import search_hard_case
from .hybrid import HybridSolver
from .research_db import ALLOWED_STATUSES, ResearchDatabase
from .switch_solver import RepresentationSwitchingSolver
from .turing_machine import load_turing_machine
from .verification import cross_check_random


def _solver(name):
    if name == "dpll":
        return DPLLSolver()

    if name == "hybrid":
        return HybridSolver()

    if name == "switch":
        return RepresentationSwitchingSolver()

    raise ValueError("Неизвестный solver")


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
        solvers=tuple(item.strip() for item in args.solvers.split(",") if item.strip()),
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


def benchmark_command(args):
    results = run_release_suite(seed=args.seed)
    csv_path, json_path, report_path = save_benchmark(
        results,
        args.output,
    )

    print("Release benchmark завершён.")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Report: {report_path}")
    print()
    print(report_path.read_text(encoding="utf-8"))


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
        use_bruteforce=args.bruteforce,
        use_reference=args.reference,
    )

    print(f"Проверено задач: {summary.checked}")
    print(f"DPLL vs Hybrid mismatches: {summary.baseline_vs_hybrid_mismatches}")
    print(f"Switch mismatches: {summary.switch_mismatches}")
    print(f"Brute-force mismatches: {summary.bruteforce_mismatches}")
    print(f"Reference mismatches: {summary.reference_mismatches}")

    all_mismatches = (
        summary.baseline_vs_hybrid_mismatches
        + summary.switch_mismatches
        + summary.bruteforce_mismatches
        + summary.reference_mismatches
    )

    print("Несовпадений не найдено." if all_mismatches == 0 else "Есть несовпадения.")


def doctor_command(args):
    result = run_doctor()

    for check in result.checks:
        print(check)

    if result.ok:
        print("Итог: установка и основные функции работают.")
        return

    print("Итог: самопроверка завершилась ошибкой.")
    raise SystemExit(1)


def turing_command(args):
    machine = load_turing_machine(args.machine)
    result = machine.run(
        args.input,
        max_steps=args.max_steps,
        trace=args.trace,
    )

    print(f"machine: {result.machine}")
    print(f"status: {result.status}")
    print(f"accepted: {result.accepted}")
    print(f"halted: {result.halted}")
    print(f"steps: {result.steps}")
    print(f"final_state: {result.final_state}")
    print(f"head: {result.head}")
    print(f"tape_start: {result.tape_start}")
    print(f"tape: {result.tape}")

    if args.trace:
        print()
        print("TRACE")

        for item in result.trace:
            print(
                f"step={item.step} "
                f"state={item.state} "
                f"head={item.head} "
                f"read={item.read} "
                f"window_start={item.window_start} "
                f"window={item.window}"
            )


def lang_command(args):
    from .labscript.cli import main as labscript_main

    labscript_main(args.lab_args)


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
    solve_parser.add_argument(
        "--solver",
        choices=["dpll", "hybrid", "switch"],
        default="switch",
    )
    solve_parser.set_defaults(handler=solve_command)

    experiment_parser = commands.add_parser("experiment", help="серия экспериментов роста")
    experiment_parser.add_argument("--start", type=int, default=10)
    experiment_parser.add_argument("--stop", type=int, default=30)
    experiment_parser.add_argument("--step", type=int, default=5)
    experiment_parser.add_argument("--repeats", type=int, default=5)
    experiment_parser.add_argument("--ratio", type=float, default=4.2)
    experiment_parser.add_argument("--seed", type=int, default=1)
    experiment_parser.add_argument("--solvers", default="dpll,hybrid,switch")
    experiment_parser.add_argument("--output", default="results/latest")
    experiment_parser.set_defaults(handler=experiment_command)

    benchmark_parser = commands.add_parser(
        "benchmark",
        help="запустить структурный release benchmark",
    )
    benchmark_parser.add_argument("--seed", type=int, default=1)
    benchmark_parser.add_argument("--output", default="results/release-benchmark")
    benchmark_parser.set_defaults(handler=benchmark_command)

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
        "--bruteforce",
        action="store_true",
        help="сверять с полным перебором; используйте только для небольшого n",
    )
    verify_parser.add_argument(
        "--reference",
        action="store_true",
        help="также сверять с optional PySAT",
    )
    verify_parser.set_defaults(handler=verify_command)

    doctor_parser = commands.add_parser(
        "doctor",
        help="быстрая самопроверка установки",
    )
    doctor_parser.set_defaults(handler=doctor_command)

    turing_parser = commands.add_parser(
        "tm",
        help="запустить детерминированную машину Тьюринга из JSON",
    )
    turing_parser.add_argument("machine", help="JSON-файл с описанием машины")
    turing_parser.add_argument("input", nargs="?", default="", help="входная строка")
    turing_parser.add_argument("--max-steps", type=int, default=10_000)
    turing_parser.add_argument("--trace", action="store_true")
    turing_parser.set_defaults(handler=turing_command)

    lang_parser = commands.add_parser(
        "lang",
        help="LabScript: run/check/debug/build bilingual programs",
    )
    lang_parser.add_argument("lab_args", nargs=argparse.REMAINDER)
    lang_parser.set_defaults(handler=lang_command)

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
