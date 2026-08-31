"""
models.py

SQLite schema for per-user, per-skill BKT mastery state.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

# Defaults mirror code/bkt_update.py's BKTParams so a first-time lookup
# behaves the same whether mastery is tracked in-memory or persisted here.
DEFAULT_PROB_MASTERY = 0.1
DEFAULT_PROB_SLIP = 0.1
DEFAULT_PROB_GUESS = 0.25
DEFAULT_PROB_TRANSIT = 0.3

CREATE_MASTERY_TABLE = """
CREATE TABLE IF NOT EXISTS mastery (
    user_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    prob_mastery REAL NOT NULL,
    prob_slip REAL NOT NULL,
    prob_guess REAL NOT NULL,
    prob_transit REAL NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, skill_id)
);
"""


@dataclass
class MasteryRecord:
    user_id: str
    skill_id: str
    prob_mastery: float = DEFAULT_PROB_MASTERY
    prob_slip: float = DEFAULT_PROB_SLIP
    prob_guess: float = DEFAULT_PROB_GUESS
    prob_transit: float = DEFAULT_PROB_TRANSIT
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "MasteryRecord":
        return cls(
            user_id=row["user_id"],
            skill_id=row["skill_id"],
            prob_mastery=row["prob_mastery"],
            prob_slip=row["prob_slip"],
            prob_guess=row["prob_guess"],
            prob_transit=row["prob_transit"],
            updated_at=row["updated_at"],
        )


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(CREATE_MASTERY_TABLE)
    conn.commit()
