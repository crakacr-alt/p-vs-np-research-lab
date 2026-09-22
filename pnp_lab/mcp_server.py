"""MCP-обёртка вокруг лаборатории.

Этот модуль не нужен для обычной работы проекта.
Он нужен только тогда, когда пользователь хочет дать модели/агенту
инструменты лаборатории через Model Context Protocol (MCP).
"""

from dataclasses import asdict

from .cnf import load_dimacs
from .experiments import run_growth_experiment, summarize_growth
from .hard_search import search_hard_case
from .hybrid import HybridSolver


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as error:
        raise RuntimeError(
            "MCP не установлен. Выполните: pip install -e \".[mcp]\""
        ) from error

    mcp = FastMCP("p-vs-np-research-lab")

    @mcp.tool()
    def project_status() -> dict:
        """Вернуть краткое состояние исследовательского проекта."""

        return {
            "version": "0.2.0",
            "goal": "Воспроизводимые эксперименты с точными SAT-алгоритмами",
            "claim": "Проект НЕ является доказательством P = NP",
            "main_solver": HybridSolver.name,
        }

    @mcp.tool()
    def solve_cnf_file(path: str) -> dict:
        """Решить локальный DIMACS CNF-файл точным hybrid solver."""

        problem = load_dimacs(path)
        return HybridSolver().solve(problem).to_dict()

    @mcp.tool()
    def growth_experiment(
        start: int = 10,
        stop: int = 30,
        step: int = 5,
        repeats: int = 3,
        ratio: float = 4.2,
        seed: int = 1,
    ) -> dict:
        """Запустить небольшой воспроизводимый эксперимент роста."""

        rows = run_growth_experiment(
            start=start,
            stop=stop,
            step=step,
            repeats=repeats,
            ratio=ratio,
            seed=seed,
            solvers=("hybrid",),
        )

        summary = summarize_growth(rows, HybridSolver.name)

        return {
            "rows": [asdict(row) for row in rows],
            "summary": summary,
        }

    @mcp.tool()
    def hunt_hard_case(
        variables: int = 20,
        clauses: int = 84,
        iterations: int = 100,
        seed: int = 1,
    ) -> dict:
        """Найти трудный стресс-тест для текущего hybrid solver."""

        case = search_hard_case(
            variables=variables,
            clauses=clauses,
            iterations=iterations,
            seed=seed,
        )

        return {
            "variables": variables,
            "clauses": clauses,
            "decisions": case.decisions,
            "calls": case.calls,
            "seconds": case.seconds,
            "sat": case.sat,
            "warning": "Это стресс-тест, а не математический контрпример P vs NP.",
        }

    return mcp


def main():
    mcp = build_server()
    mcp.run()


if __name__ == "__main__":
    main()
