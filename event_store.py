"""Append-only SQLite event history store, with periodic state checkpoints."""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_DB_PATH = Path(__file__).with_name("events.db")
DEFAULT_CHECKPOINT_INTERVAL = 5
DEFAULT_BUSY_TIMEOUT = 30.0

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Event:
    id: int
    description: str
    happened_at: str
    change_data: Any
    confidence: float
    created_at: str


@dataclass(frozen=True)
class Checkpoint:
    id: int
    happened_at: str
    last_event_id: int
    event_count: int
    state_data: Any
    size_bytes: int
    created_at: str


StateMerger = Callable[[dict, "Event"], dict]


def default_merge_state(state, event):
    merged = dict(state)
    merged.update(event.change_data)
    return merged


_STATE_MERGE_FN: StateMerger = default_merge_state


def set_state_merge_function(fn=None):
    global _STATE_MERGE_FN
    _STATE_MERGE_FN = fn if fn is not None else default_merge_state


def _connect(db_path=DEFAULT_DB_PATH):
    connection = sqlite3.connect(str(db_path), timeout=DEFAULT_BUSY_TIMEOUT, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute(f"PRAGMA busy_timeout = {int(DEFAULT_BUSY_TIMEOUT * 1000)}")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def _normalise_datetime(value):
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    elif isinstance(value, datetime):
        parsed = value
    else:
        raise TypeError("Date/time must be a datetime or ISO-8601 string.")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds")


def initialize_database(db_path=DEFAULT_DB_PATH):
    schema = """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        happened_at TEXT NOT NULL,
        change_data TEXT NOT NULL DEFAULT '{}',
        confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    );
    CREATE INDEX IF NOT EXISTS idx_events_happened_at ON events (happened_at);
    CREATE TRIGGER IF NOT EXISTS events_prevent_update BEFORE UPDATE ON events
    BEGIN SELECT RAISE(ABORT, 'events table is append-only: updates are forbidden'); END;
    CREATE TRIGGER IF NOT EXISTS events_prevent_delete BEFORE DELETE ON events
    BEGIN SELECT RAISE(ABORT, 'events table is append-only: deletes are forbidden'); END;

    CREATE TABLE IF NOT EXISTS checkpoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        happened_at TEXT NOT NULL,
        last_event_id INTEGER NOT NULL,
        event_count INTEGER NOT NULL,
        state_data TEXT NOT NULL DEFAULT '{}',
        size_bytes INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    );
    CREATE INDEX IF NOT EXISTS idx_checkpoints_happened_at ON checkpoints (happened_at);
    CREATE INDEX IF NOT EXISTS idx_checkpoints_last_event_id ON checkpoints (last_event_id);
    CREATE TRIGGER IF NOT EXISTS checkpoints_prevent_update BEFORE UPDATE ON checkpoints
    BEGIN SELECT RAISE(ABORT, 'checkpoints table is append-only: updates are forbidden'); END;
    CREATE TRIGGER IF NOT EXISTS checkpoints_prevent_delete BEFORE DELETE ON checkpoints
    BEGIN SELECT RAISE(ABORT, 'checkpoints table is append-only: deletes are forbidden'); END;
    """
    connection = _connect(db_path)
    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()


def add_event(description, happened_at, change_data, confidence,
              db_path=DEFAULT_DB_PATH, auto_checkpoint=True,
              checkpoint_interval=DEFAULT_CHECKPOINT_INTERVAL):
    if not description or not description.strip():
        raise ValueError("description must not be empty")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")
    if not isinstance(change_data, dict):
        raise TypeError(f"change_data must be a dict; got {type(change_data).__name__}")

    initialize_database(db_path)
    timestamp = _normalise_datetime(happened_at)
    serialised_change = json.dumps(change_data, ensure_ascii=False, sort_keys=True)

    connection = _connect(db_path)
    try:
        cursor = connection.execute(
            "INSERT INTO events (description, happened_at, change_data, confidence) VALUES (?, ?, ?, ?)",
            (description.strip(), timestamp, serialised_change, confidence),
        )
        connection.commit()
        new_id = int(cursor.lastrowid)
    finally:
        connection.close()

    if auto_checkpoint and checkpoint_interval > 0:
        create_checkpoint(db_path, min_new_events=checkpoint_interval)

    return new_id


def fetch_events_between(start, end, db_path=DEFAULT_DB_PATH):
    initialize_database(db_path)
    start_value = _normalise_datetime(start)
    end_value = _normalise_datetime(end)
    if start_value > end_value:
        raise ValueError("start must be earlier than or equal to end")
    connection = _connect(db_path)
    try:
        rows = connection.execute(
            "SELECT id, description, happened_at, change_data, confidence, created_at "
            "FROM events WHERE happened_at BETWEEN ? AND ? ORDER BY happened_at ASC, id ASC",
            (start_value, end_value),
        ).fetchall()
    finally:
        connection.close()
    return [_row_to_event(row) for row in rows]


def _row_to_event(row):
    return Event(
        id=row["id"], description=row["description"], happened_at=row["happened_at"],
        change_data=json.loads(row["change_data"]), confidence=row["confidence"],
        created_at=row["created_at"],
    )


def _row_to_checkpoint(row):
    return Checkpoint(
        id=row["id"], happened_at=row["happened_at"], last_event_id=row["last_event_id"],
        event_count=row["event_count"], state_data=json.loads(row["state_data"]),
        size_bytes=row["size_bytes"], created_at=row["created_at"],
    )


def _fold_state(events, base_state=None, merge_fn=None):
    merge = merge_fn if merge_fn is not None else _STATE_MERGE_FN
    state = dict(base_state) if base_state else {}
    for event in events:
        state = merge(state, event)
    return state


def _latest_checkpoint_last_event_id(connection):
    row = connection.execute("SELECT last_event_id FROM checkpoints ORDER BY id DESC LIMIT 1").fetchone()
    return int(row["last_event_id"]) if row else 0


def create_checkpoint(db_path=DEFAULT_DB_PATH, min_new_events=1, merge_fn=None):
    initialize_database(db_path)
    connection = _connect(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        last_checkpoint_row = connection.execute(
            "SELECT last_event_id, state_data FROM checkpoints ORDER BY id DESC LIMIT 1"
        ).fetchone()
        last_event_id = int(last_checkpoint_row["last_event_id"]) if last_checkpoint_row else 0
        base_state = json.loads(last_checkpoint_row["state_data"]) if last_checkpoint_row else {}

        rows = connection.execute(
            "SELECT id, description, happened_at, change_data, confidence, created_at "
            "FROM events WHERE id > ? ORDER BY id ASC",
            (last_event_id,),
        ).fetchall()

        if len(rows) < max(min_new_events, 1):
            connection.execute("ROLLBACK")
            return None

        new_events = [_row_to_event(row) for row in rows]
        new_state = _fold_state(new_events, base_state, merge_fn=merge_fn)
        serialised_state = json.dumps(new_state, ensure_ascii=False, sort_keys=True)
        size_bytes = len(serialised_state.encode("utf-8"))

        cursor = connection.execute(
            "INSERT INTO checkpoints (happened_at, last_event_id, event_count, state_data, size_bytes) "
            "VALUES (?, ?, ?, ?, ?)",
            (new_events[-1].happened_at, new_events[-1].id, len(new_events), serialised_state, size_bytes),
        )
        connection.commit()
        return int(cursor.lastrowid)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def fetch_latest_checkpoint_before(timestamp, db_path=DEFAULT_DB_PATH):
    initialize_database(db_path)
    timestamp_value = _normalise_datetime(timestamp)
    connection = _connect(db_path)
    try:
        row = connection.execute(
            "SELECT id, happened_at, last_event_id, event_count, state_data, size_bytes, created_at "
            "FROM checkpoints WHERE happened_at <= ? ORDER BY happened_at DESC, id DESC LIMIT 1",
            (timestamp_value,),
        ).fetchone()
    finally:
        connection.close()
    return _row_to_checkpoint(row) if row else None


def get_state_at(timestamp, db_path=DEFAULT_DB_PATH, merge_fn=None):
    timestamp_value = _normalise_datetime(timestamp)
    checkpoint = fetch_latest_checkpoint_before(timestamp_value, db_path)
    base_state = checkpoint.state_data if checkpoint else {}
    since_event_id = checkpoint.last_event_id if checkpoint else 0

    initialize_database(db_path)
    connection = _connect(db_path)
    try:
        rows = connection.execute(
            "SELECT id, description, happened_at, change_data, confidence, created_at "
            "FROM events WHERE id > ? AND happened_at <= ? ORDER BY id ASC",
            (since_event_id, timestamp_value),
        ).fetchall()
    finally:
        connection.close()

    remaining_events = [_row_to_event(row) for row in rows]
    return _fold_state(remaining_events, base_state, merge_fn=merge_fn)


def get_storage_stats(db_path=DEFAULT_DB_PATH):
    initialize_database(db_path)
    connection = _connect(db_path)
    try:
        event_rows = connection.execute("SELECT description, change_data FROM events").fetchall()
        checkpoint_rows = connection.execute("SELECT size_bytes FROM checkpoints").fetchall()
    finally:
        connection.close()

    event_count = len(event_rows)
    if event_count:
        total_event_bytes = sum(
            len(row["description"].encode("utf-8")) + len(row["change_data"].encode("utf-8"))
            for row in event_rows
        )
        avg_event_bytes = total_event_bytes / event_count
    else:
        avg_event_bytes = 0.0

    checkpoint_count = len(checkpoint_rows)
    avg_checkpoint_bytes = (
        sum(row["size_bytes"] for row in checkpoint_rows) / checkpoint_count
        if checkpoint_count else 0.0
    )
    db_file_bytes = Path(db_path).stat().st_size if Path(db_path).exists() else 0

    return {
        "event_count": event_count, "checkpoint_count": checkpoint_count,
        "avg_event_bytes": avg_event_bytes, "avg_checkpoint_bytes": avg_checkpoint_bytes,
        "db_file_bytes": db_file_bytes,
    }
