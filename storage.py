import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "runs.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api TEXT NOT NULL,
                summary TEXT NOT NULL,
                tests TEXT NOT NULL
            )
            """
        )


def save_run(run_data: dict) -> None:
    init_db()
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO runs (timestamp, api, summary, tests) VALUES (?, ?, ?, ?)",
            (
                run_data["timestamp"],
                run_data["api"],
                json.dumps(run_data["summary"]),
                json.dumps(run_data["tests"]),
            ),
        )


def list_runs(limit: int = 20) -> list[dict]:
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, timestamp, api, summary, tests FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    runs = []
    for row in rows:
        runs.append(
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "api": row["api"],
                "summary": json.loads(row["summary"]),
                "tests": json.loads(row["tests"]),
            }
        )
    return runs


def get_last_run() -> dict | None:
    init_db()
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id, timestamp, api, summary, tests FROM runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "api": row["api"],
        "summary": json.loads(row["summary"]),
        "tests": json.loads(row["tests"]),
    }
