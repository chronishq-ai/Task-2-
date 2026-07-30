# Append-Only Event History Store (v0.2)

This project stores every event permanently in a local SQLite database, and
periodically folds events into **checkpoints** so old history can be
summarized without replaying it from the beginning.

## Files

- `event_store.py` — database setup, `add_event()`, `fetch_events_between()`,
  and the checkpoint functions below
- `seed_events.py` — inserts 24 fictional sample events spread across ~5
  weeks, so several checkpoints get created automatically
- `demo_query.py` — demonstrates date-range retrieval, checkpoint lookup,
  and state reconstruction
- `test_event_store.py` — verifies querying, append-only protection, and
  checkpoint behavior (9 tests)
- `events.db` — created automatically

## Tables

### `events`

| Column | Meaning |
|---|---|
| `id` | Unique event ID |
| `description` | What happened |
| `happened_at` | When it happened |
| `change_data` | JSON describing what changed |
| `confidence` | Score from 0.0 to 1.0 |
| `created_at` | When the event was inserted |

### `checkpoints`

| Column | Meaning |
|---|---|
| `id` | Unique checkpoint ID |
| `happened_at` | Timestamp of the last event folded into this checkpoint |
| `last_event_id` | ID of the last event folded into this checkpoint |
| `event_count` | How many events this checkpoint folded in (since the previous checkpoint) |
| `state_data` | JSON: all folded `change_data`, merged key-by-key, later events win |
| `size_bytes` | Size of `state_data` in bytes, measured at insert time |
| `created_at` | When the checkpoint row was inserted |

Both tables are append-only: `UPDATE` and `DELETE` are blocked by SQLite
triggers, in addition to there being no update/delete functions in the code.

## Checkpoints

- **Automatic:** `add_event()` checks how many events have arrived since the
  last checkpoint, and calls `create_checkpoint()` once that reaches
  `DEFAULT_CHECKPOINT_INTERVAL` (5, by default). Pass
  `checkpoint_interval=` to `add_event()` to change this, or
  `auto_checkpoint=False` to disable it.
- **Manual:** call `create_checkpoint(db_path)` any time to fold in whatever
  events have accumulated since the last checkpoint (or from the start, if
  none exists yet). Returns `None` if there's nothing new to fold in.
- **Lookup:** `fetch_latest_checkpoint_before(timestamp, db_path)` returns
  the most recent `Checkpoint` at or before a given time, or `None`.
- **State reconstruction:** `get_state_at(timestamp, db_path)` returns the
  folded state as of a given time. It starts from the nearest checkpoint
  and replays only the events after it, rather than replaying the entire
  history — this is the main reason checkpoints exist.
- **Storage estimation:** `get_storage_stats(db_path)` reports average
  event/checkpoint sizes from the current data; `estimate_storage_for_years()`
  projects total storage at a steady event rate.

Folding is a simple shallow merge of each event's `change_data` dict, with
later events overwriting matching keys from earlier ones. This is a
generic default — a domain-specific store might instead scope keys per
entity (e.g. per `project_id`) to avoid unrelated events colliding on the
same key name.

## Run in PowerShell

```powershell
python seed_events.py
python demo_query.py
python -m unittest test_event_store.py
```

## Expected `seed_events.py` output (values will vary slightly)

```text
Inserted 24 events into ...\events.db
Created 4 checkpoints
Checkpoint size: 210 bytes (average)
Estimated storage for 10 years: 1.02 MB
```

## Expected test result

```text
Ran 9 tests

OK
```

## Future schema growth

New nullable columns or columns with defaults can be added later to either
table, e.g.:

```sql
ALTER TABLE events ADD COLUMN source TEXT;
ALTER TABLE checkpoints ADD COLUMN schema_version INTEGER DEFAULT 1;
```

Existing rows will remain valid. `state_data` is stored as JSON text
specifically so its shape can evolve without a migration.
