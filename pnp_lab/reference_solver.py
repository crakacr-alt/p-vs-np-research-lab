from .cnf import CNFProblem


def solve_with_pysat(problem: CNFProblem):
    """Независимо решает CNF через библиотеку python-sat."""

    try:
        from pysat.solvers import Solver
    except ImportError as error:
        raise RuntimeError(
            "Для reference solver установите optional dependency: "
            "pip install -e \".[reference]\""
        ) from error

    clauses = [list(clause) for clause in problem.clauses]

    with Solver(name="glucose3", bootstrap_with=clauses) as solver:
        sat = solver.solve()

        if not sat:
            return False, {}

        raw_model = solver.get_model() or []
        model = {
            abs(literal): literal > 0
            for literal in raw_model
            if abs(literal) <= problem.variables
        }

        return True, model
