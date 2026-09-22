import argparse

from .cnf import load_dimacs
from .counterexample import find_hard_random_case
from .dpll import DPLLSolver
from .experiment import run_growth_experiment


def print_model(model):
    """Красиво печатает значения переменных."""

    if not model:
        print("Модель пуста.")
        return

    parts = []

    for variable in sorted(model):
        if model[variable]:
            value = "1"
        else:
            value = "0"

        parts.append(
            f"x{variable}={value}"
        )

    print(
        "Модель:",
        ", ".join(parts),
    )


def solve_command(path):
    problem = load_dimacs(path)
    result = DPLLSolver().solve(problem)

    if result.sat:
        print("SAT")
    else:
        print("UNSAT")

    print(
        f"Решений о ветвлении: {result.decisions}"
    )
    print(
        f"Рекурсивных вызовов: {result.calls}"
    )
    print(
        f"Время: {result.seconds:.6f} сек."
    )

    if result.sat:
        print_model(result.model)


def experiment_command(args):
    rows = run_growth_experiment(
        start=args.start,
        stop=args.stop,
        step=args.step,
        ratio=args.ratio,
        seed=args.seed,
    )

    print(
        "n\tclauses\tSAT\tdecisions\tcalls\tseconds"
    )

    for row in rows:
        print(
            f"{row.variables}\t"
            f"{row.clauses}\t"
            f"{row.sat}\t"
            f"{row.decisions}\t"
            f"{row.calls}\t"
            f"{row.seconds:.6f}"
        )


def hunt_command(args):
    case = find_hard_random_case(
        variables=args.variables,
        tries=args.tries,
        ratio=args.ratio,
        seed_start=args.seed_start,
    )

    print("Самый трудный найденный случай:")
    print(f"seed: {case.seed}")
    print(f"переменных: {case.variables}")
    print(f"клауз: {case.clauses}")
    print(f"SAT: {case.sat}")
    print(f"ветвлений: {case.decisions}")
    print(f"вызовов: {case.calls}")
    print(f"время: {case.seconds:.6f} сек.")


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "P vs NP Research Lab: "
            "учебные эксперименты с SAT"
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    solve_parser = subparsers.add_parser(
        "solve",
        help="решить DIMACS CNF-файл",
    )

    solve_parser.add_argument(
        "file",
        help="путь к .cnf файлу",
    )

    experiment_parser = subparsers.add_parser(
        "experiment",
        help="эксперимент роста сложности",
    )

    experiment_parser.add_argument(
        "--start",
        type=int,
        default=10,
    )
    experiment_parser.add_argument(
        "--stop",
        type=int,
        default=30,
    )
    experiment_parser.add_argument(
        "--step",
        type=int,
        default=5,
    )
    experiment_parser.add_argument(
        "--ratio",
        type=float,
        default=4.2,
    )
    experiment_parser.add_argument(
        "--seed",
        type=int,
        default=1,
    )

    hunt_parser = subparsers.add_parser(
        "hunt",
        help="найти трудный случай для текущего DPLL",
    )

    hunt_parser.add_argument(
        "--variables",
        type=int,
        default=20,
    )
    hunt_parser.add_argument(
        "--tries",
        type=int,
        default=100,
    )
    hunt_parser.add_argument(
        "--ratio",
        type=float,
        default=4.2,
    )
    hunt_parser.add_argument(
        "--seed-start",
        type=int,
        default=1,
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "solve":
        solve_command(args.file)

    elif args.command == "experiment":
        experiment_command(args)

    elif args.command == "hunt":
        hunt_command(args)


if __name__ == "__main__":
    main()
