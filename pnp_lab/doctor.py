from dataclasses import dataclass

from .benchmarks import xor_inconsistent_core
from .cnf import CNFProblem, model_satisfies
from .dpll import DPLLSolver
from .hybrid import HybridSolver
from .switch_solver import RepresentationSwitchingSolver
from .turing_machine import Transition, TuringMachine


@dataclass
class DoctorResult:
    ok: bool
    checks: list[str]


def run_doctor():
    """Быстрая самопроверка установки и основных solver-ов."""

    checks = []

    sat_problem = CNFProblem(
        variables=3,
        clauses=((1, 2), (-1, 3), (-2, 3)),
    )
    unsat_problem = CNFProblem(
        variables=1,
        clauses=((1,), (-1,)),
    )

    for solver in (
        DPLLSolver(),
        HybridSolver(),
        RepresentationSwitchingSolver(),
    ):
        sat_result = solver.solve(sat_problem)

        if not sat_result.sat:
            return DoctorResult(False, checks + [f"{solver.name}: SAT test failed"])

        if not model_satisfies(sat_problem, sat_result.model):
            return DoctorResult(False, checks + [f"{solver.name}: model check failed"])

        unsat_result = solver.solve(unsat_problem)

        if unsat_result.sat:
            return DoctorResult(False, checks + [f"{solver.name}: UNSAT test failed"])

        checks.append(f"{solver.name}: basic SAT/UNSAT OK")

    xor_result = RepresentationSwitchingSolver().solve(
        xor_inconsistent_core()
    )

    if xor_result.sat:
        return DoctorResult(False, checks + ["XOR contradiction test failed"])

    if xor_result.metrics.xor_equations_detected < 1:
        return DoctorResult(False, checks + ["XOR detection did not activate"])

    checks.append("representation switch CNF -> XOR: OK")

    machine = TuringMachine(
        name="doctor-tm",
        states={"q0", "qa"},
        input_alphabet={"1"},
        tape_alphabet={"1", "_"},
        blank="_",
        start_state="q0",
        accept_states={"qa"},
        reject_states=set(),
        transitions={
            ("q0", "1"): Transition("1", "S", "qa"),
        },
    )
    tm_result = machine.run("1")

    if tm_result.status != "ACCEPT":
        return DoctorResult(False, checks + ["Turing Machine self-test failed"])

    checks.append("deterministic Turing Machine: OK")

    return DoctorResult(True, checks)
