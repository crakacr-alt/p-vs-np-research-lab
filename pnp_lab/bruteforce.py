from itertools import product

from .cnf import CNFProblem, model_satisfies


def solve_bruteforce(problem: CNFProblem, max_variables: int = 24):
    """Маленький эталонный solver полным перебором.

    Он намеренно медленный. Его задача — не производительность, а независимая
    проверка более сложных solver-ов на небольших формулах.
    """

    if problem.variables > max_variables:
        raise ValueError(
            f"Brute force ограничен {max_variables} переменными, "
            f"получено {problem.variables}"
        )

    for values in product([False, True], repeat=problem.variables):
        model = {
            index + 1: value
            for index, value in enumerate(values)
        }

        if model_satisfies(problem, model):
            return True, model

    return False, {}
