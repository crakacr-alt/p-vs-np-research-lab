"""MCP-интерфейс научной лаборатории.

MCP позволяет модели запускать только явно опубликованные инструменты.
Файловые операции ограничены PNP_LAB_WORKSPACE.
"""

from dataclasses import asdict

from .benchmark_runner import run_release_suite, save_benchmark
from .cnf import load_dimacs, save_dimacs
from .doctor import run_doctor
from .experiments import run_growth_experiment, summarize_growth
from .hard_search import search_hard_case
from .research_db import ResearchDatabase
from .switch_solver import RepresentationSwitchingSolver
from .workspace import safe_workspace_path


def build_server():
    try:
        from mcp.server import MCPServer
    except ImportError as error:
        raise RuntimeError(
            'MCP SDK 2.x не установлен. Выполните: pip install -e ".[mcp]"'
        ) from error

    mcp = MCPServer("p-vs-np-research-lab")

    @mcp.tool()
    def project_status() -> dict:
        """Вернуть научный статус и версию проекта."""

        return {
            "version": "1.0.0",
            "goal": "Воспроизводимые эксперименты с точными SAT-алгоритмами",
            "main_solver": RepresentationSwitchingSolver.name,
            "implemented_switch": "точное распознавание 3-CNF XOR -> GF(2)",
            "claim": "Проект НЕ является доказательством P = NP или P != NP",
        }

    @mcp.tool()
    def doctor() -> dict:
        """Быстро проверить основные функции лаборатории."""

        result = run_doctor()
        return asdict(result)

    @mcp.tool()
    def solve_cnf_file(path: str) -> dict:
        """Решить DIMACS CNF внутри разрешённого workspace."""

        safe_path = safe_workspace_path(path)
        problem = load_dimacs(safe_path)
        return RepresentationSwitchingSolver().solve(problem).to_dict()

    @mcp.tool()
    def growth_experiment(
        start: int = 10,
        stop: int = 30,
        step: int = 5,
        repeats: int = 3,
        ratio: float = 4.2,
        seed: int = 1,
    ) -> dict:
        """Запустить воспроизводимый эксперимент роста."""

        rows = run_growth_experiment(
            start=start,
            stop=stop,
            step=step,
            repeats=repeats,
            ratio=ratio,
            seed=seed,
            solvers=("switch",),
        )

        summary = summarize_growth(
            rows,
            RepresentationSwitchingSolver.name,
        )

        return {
            "rows": [asdict(row) for row in rows],
            "summary": summary,
        }

    @mcp.tool()
    def run_structural_benchmark(
        output_dir: str = "results/mcp-benchmark",
        seed: int = 1,
    ) -> dict:
        """Запустить release benchmark и сохранить CSV/JSON/Markdown."""

        output = safe_workspace_path(output_dir)
        results = run_release_suite(seed=seed)
        csv_path, json_path, report_path = save_benchmark(results, output)

        return {
            "rows": [asdict(row) for row in results],
            "csv": str(csv_path),
            "json": str(json_path),
            "report": str(report_path),
        }

    @mcp.tool()
    def hunt_hard_case(
        variables: int = 20,
        clauses: int = 84,
        iterations: int = 100,
        seed: int = 1,
        output_file: str = "results/mcp-hard-case.cnf",
    ) -> dict:
        """Найти и сохранить трудный стресс-тест."""

        case = search_hard_case(
            variables=variables,
            clauses=clauses,
            iterations=iterations,
            seed=seed,
        )

        output = safe_workspace_path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        save_dimacs(case.problem, output)

        return {
            "variables": variables,
            "clauses": clauses,
            "decisions": case.decisions,
            "calls": case.calls,
            "seconds": case.seconds,
            "sat": case.sat,
            "saved": str(output),
            "warning": "Это стресс-тест, а не математический контрпример P vs NP.",
        }

    @mcp.tool()
    def add_hypothesis(
        title: str,
        statement: str,
        notes: str = "",
        database: str = "research/research.db",
    ) -> dict:
        """Добавить проверяемую исследовательскую гипотезу."""

        db_path = safe_workspace_path(database)
        db = ResearchDatabase(db_path)
        hypothesis_id = db.add_hypothesis(title, statement, notes)

        return {
            "id": hypothesis_id,
            "status": "IDEA",
        }

    @mcp.tool()
    def list_hypotheses(
        database: str = "research/research.db",
    ) -> list[dict]:
        """Получить журнал гипотез."""

        db_path = safe_workspace_path(database)
        db = ResearchDatabase(db_path)

        return [
            asdict(item)
            for item in db.list_hypotheses()
        ]

    @mcp.tool()
    def set_hypothesis_status(
        hypothesis_id: int,
        status: str,
        notes: str = "",
        database: str = "research/research.db",
    ) -> dict:
        """Изменить статус гипотезы без автоматического PROVED."""

        db_path = safe_workspace_path(database)
        db = ResearchDatabase(db_path)
        db.set_status(
            hypothesis_id,
            status,
            notes or None,
        )

        return {
            "id": hypothesis_id,
            "status": status,
        }

    return mcp


def main():
    mcp = build_server()
    mcp.run()


if __name__ == "__main__":
    main()
