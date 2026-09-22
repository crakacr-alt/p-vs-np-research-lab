import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_STATUSES = {
    "IDEA",
    "TESTING",
    "SURVIVED_TESTS",
    "COUNTEREXAMPLE_FOUND",
    "REJECTED",
    "PROOF_CANDIDATE",
}


@dataclass
class Hypothesis:
    id: int
    title: str
    statement: str
    status: str
    notes: str
    created_at: str
    updated_at: str


class ResearchDatabase:
    """Минимальная SQLite-память научного проекта."""

    def __init__(self, path="research/research.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _create_tables(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS hypotheses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    statement TEXT NOT NULL,
                    status TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def add_hypothesis(self, title, statement, notes="") -> int:
        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO hypotheses(title, statement, status, notes, created_at, updated_at)
                VALUES (?, ?, 'IDEA', ?, ?, ?)
                """,
                (title, statement, notes, now, now),
            )
            return cursor.lastrowid

    def list_hypotheses(self):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, statement, status, notes, created_at, updated_at
                FROM hypotheses
                ORDER BY id
                """
            ).fetchall()

        return [Hypothesis(*row) for row in rows]

    def set_status(self, hypothesis_id: int, status: str, notes: str | None = None):
        if status not in ALLOWED_STATUSES:
            raise ValueError(
                "Недопустимый статус. Допустимые: " + ", ".join(sorted(ALLOWED_STATUSES))
            )

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            if notes is None:
                connection.execute(
                    "UPDATE hypotheses SET status=?, updated_at=? WHERE id=?",
                    (status, now, hypothesis_id),
                )
            else:
                connection.execute(
                    "UPDATE hypotheses SET status=?, notes=?, updated_at=? WHERE id=?",
                    (status, notes, now, hypothesis_id),
                )
