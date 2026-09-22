from dataclasses import dataclass

from .cnf import CNFProblem
from .generator import random_3sat
from .xor import XOREquation, xor3_to_cnf


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    family: str
    problem: CNFProblem
    expected_sat: bool | None
    description: str


def pigeonhole(pigeons: int, holes: int) -> CNFProblem:
    """Принцип Дирихле (Pigeonhole Principle) в CNF.

    Каждый голубь должен попасть хотя бы в одну ячейку.
    В одной ячейке не может быть двух разных голубей.
    """

    if pigeons < 1 or holes < 1:
        raise ValueError("pigeons и holes должны быть положительными")

    def variable(pigeon, hole):
        return pigeon * holes + hole + 1

    clauses = []

    # Каждый голубь находится хотя бы в одной ячейке.
    for pigeon in range(pigeons):
        clauses.append(
            tuple(variable(pigeon, hole) for hole in range(holes))
        )

    # В одной ячейке не может быть двух голубей.
    for hole in range(holes):
        for first in range(pigeons):
            for second in range(first + 1, pigeons):
                clauses.append(
                    (
                        -variable(first, hole),
                        -variable(second, hole),
                    )
                )

    return CNFProblem(
        variables=pigeons * holes,
        clauses=tuple(clauses),
    )


def independent_blocks(blocks: int) -> CNFProblem:
    """Создаёт CNF из независимых небольших компонент."""

    if blocks < 1:
        raise ValueError("blocks должен быть положительным")

    clauses = []

    for block in range(blocks):
        a = block * 3 + 1
        b = block * 3 + 2
        c = block * 3 + 3

        clauses.extend(
            [
                (a, b, c),
                (-a, b, c),
                (a, -b, c),
                (a, b, -c),
            ]
        )

    return CNFProblem(
        variables=blocks * 3,
        clauses=tuple(clauses),
    )


def xor_chain(length: int) -> CNFProblem:
    """Создаёт SAT-задачу из цепочки точных XOR-ограничений."""

    if length < 1:
        raise ValueError("length должен быть положительным")

    clauses = []

    for index in range(length):
        equation = XOREquation(
            variables=(index + 1, index + 2, index + 3),
            rhs=bool(index % 2),
        )
        clauses.extend(xor3_to_cnf(equation))

    return CNFProblem(
        variables=length + 2,
        clauses=tuple(clauses),
    )


def xor_inconsistent_core() -> CNFProblem:
    """Небольшая UNSAT XOR-система с линейной зависимостью.

    Четыре левых части в сумме по XOR дают 0, а правые части дают 1.
    Значит система противоречива.
    """

    equations = [
        XOREquation((1, 2, 3), False),
        XOREquation((1, 4, 5), False),
        XOREquation((2, 4, 6), False),
        XOREquation((3, 5, 6), True),
    ]

    clauses = []

    for equation in equations:
        clauses.extend(xor3_to_cnf(equation))

    return CNFProblem(
        variables=6,
        clauses=tuple(clauses),
    )


def release_suite(seed: int = 1):
    """Небольшой набор разных структур для регулярной проверки релиза."""

    return [
        BenchmarkCase(
            name="random-3sat-20",
            family="random-3sat",
            problem=random_3sat(20, 84, seed=seed),
            expected_sat=None,
            description="Случайная 3-SAT около области фазового перехода.",
        ),
        BenchmarkCase(
            name="independent-8",
            family="decomposition",
            problem=independent_blocks(8),
            expected_sat=True,
            description="Независимые компоненты: проверка decomposition.",
        ),
        BenchmarkCase(
            name="php-4-3",
            family="pigeonhole",
            problem=pigeonhole(4, 3),
            expected_sat=False,
            description="Классический небольшой UNSAT Pigeonhole Principle.",
        ),
        BenchmarkCase(
            name="xor-chain-8",
            family="xor",
            problem=xor_chain(8),
            expected_sat=True,
            description="Цепочка XOR-блоков, кодированных в 3-CNF.",
        ),
        BenchmarkCase(
            name="xor-inconsistent-core",
            family="xor",
            problem=xor_inconsistent_core(),
            expected_sat=False,
            description="Линейно противоречивая XOR-система.",
        ),
    ]
