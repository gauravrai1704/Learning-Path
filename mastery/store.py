"""
store.py

Persistent (SQLite) read/write functions for per-user, per-skill mastery.

Exposes:
    get_mastery(user_id, skill_id) -> float
    set_mastery(user_id, skill_id, value) -> None
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from models import MasteryRecord, init_db

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "mastery.db"


def _connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_bkt_params(
    user_id: str,
    skill_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> MasteryRecord:
    """Return the stored BKT parameters, or defaults if never recorded."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM mastery WHERE user_id = ? AND skill_id = ?",
            (user_id, skill_id),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return MasteryRecord(user_id=user_id, skill_id=skill_id)

    return MasteryRecord.from_row(row)


def set_bkt_params(record: MasteryRecord, db_path: Path = DEFAULT_DB_PATH) -> None:
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO mastery
                (user_id, skill_id, prob_mastery, prob_slip, prob_guess, prob_transit, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, skill_id) DO UPDATE SET
                prob_mastery = excluded.prob_mastery,
                prob_slip = excluded.prob_slip,
                prob_guess = excluded.prob_guess,
                prob_transit = excluded.prob_transit,
                updated_at = excluded.updated_at
            """,
            (
                record.user_id,
                record.skill_id,
                record.prob_mastery,
                record.prob_slip,
                record.prob_guess,
                record.prob_transit,
                _now(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_mastery(
    user_id: str,
    skill_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> float:
    return get_bkt_params(user_id, skill_id, db_path).prob_mastery


def set_mastery(
    user_id: str,
    skill_id: str,
    value: float,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"prob_mastery must be within [0, 1], got {value}")

    existing = get_bkt_params(user_id, skill_id, db_path)
    existing.prob_mastery = value
    set_bkt_params(existing, db_path)


def _update_mastery(
    prob_mastery: float,
    prob_slip: float,
    prob_guess: float,
    prob_transit: float,
    is_correct: bool,
) -> float:
    """Standard BKT posterior update. Mirrors code/bkt_update.update_mastery
    so persisted results stay consistent with the in-memory reference impl.
    """
    if is_correct:
        numerator = prob_mastery * (1 - prob_slip)
        mastery_and_guess = (1 - prob_mastery) * prob_guess
    else:
        numerator = prob_mastery * prob_slip
        mastery_and_guess = (1 - prob_mastery) * (1 - prob_guess)

    posterior = numerator / (numerator + mastery_and_guess)
    return posterior + (1 - posterior) * prob_transit


class PersistentMasteryStore:
    """SQLite-backed drop-in replacement for code/bkt_update.MasteryStore.

    Matches its interface (get_mastery, record_quiz_result, is_mastered) so
    graph/nodes.py can swap the in-memory MasteryStore for this once ready:

        from mastery.store import PersistentMasteryStore as MasteryStore
    """

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path: Path = db_path

    def get_mastery(self, user_id: str, skill_id: str) -> float:
        return get_mastery(user_id, skill_id, self.db_path)

    def record_quiz_result(self, user_id: str, skill_id: str, is_correct: bool) -> float:
        params = get_bkt_params(user_id, skill_id, self.db_path)
        params.prob_mastery = _update_mastery(
            params.prob_mastery,
            params.prob_slip,
            params.prob_guess,
            params.prob_transit,
            is_correct,
        )
        set_bkt_params(params, self.db_path)
        return params.prob_mastery

    def is_mastered(self, user_id: str, skill_id: str, threshold: float = 0.6) -> bool:
        return self.get_mastery(user_id, skill_id) >= threshold
