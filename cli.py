#!/usr/bin/env python3
"""
chronis-ai — Pod E: Personal Memory Assistant CLI

Commands:
    add-event   Add a new event
    query       Ask what the system believed at a given point in time
    demo        Run the full scripted demo scenario automatically

PLACEHOLDER functions stand in for pods that haven't landed real code yet.
Pod D's real v0.2 code (pod_d_final.py) is now wired in via an adapter —
see ADAPTER section below.
"""

import argparse
import json
import random
from datetime import datetime, timedelta

# Pod D's real code (v0.2 backward smoothing) — replaces our placeholder.
import pod_d_final

# Pod B's real code (v0.2 calibration) — used with automatic fallback to
# our placeholder if the import fails or any API call errors out, so a
# missing key / rate limit / network issue never breaks the demo.
try:
    from analyzer import analyze_event as _pod_b_analyze_event
    POD_B_AVAILABLE = True
except Exception as _pod_b_import_error:
    POD_B_AVAILABLE = False
    _pod_b_import_error_msg = str(_pod_b_import_error)

# Pod C's real code (v0.2 checkpointed SQLite storage) — used as an
# ADDITIONAL durable log alongside our existing events.json. Our own
# query/then/now logic keeps running off events.json + Pod D unchanged,
# so a Pod C failure can never break the working pipeline — it only means
# that one event didn't also get a SQLite copy.
try:
    import event_store as pod_c_store
    POD_C_AVAILABLE = True
except Exception as _pod_c_import_error:
    POD_C_AVAILABLE = False
    _pod_c_import_error_msg = str(_pod_c_import_error)

# ---------------------------------------------------------------------------
# SHARED CONTRACT
# ---------------------------------------------------------------------------

VARIABLES = {
    "mood":                {"range": (0, 10), "speed": "fast"},
    "focus":               {"range": (0, 10), "speed": "fast"},
    "stress":              {"range": (0, 10), "speed": "fast"},
    "confidence":          {"range": (0, 10), "speed": "slow"},
    "trust":               {"range": (0, 10), "speed": "slow"},
    "motivation":          {"range": (0, 10), "speed": "fast"},
    "social_engagement":   {"range": (0, 10), "speed": "slow"},
}

STARTING_STATE = {name: 5.0 for name in VARIABLES}

EVENTS_FILE = "events.json"


def load_events():
    try:
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: {EVENTS_FILE} was corrupted or empty — starting fresh.")
        return []


def save_events(events):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)


EVENT_LOG = load_events()


# ---------------------------------------------------------------------------
# PLACEHOLDER — Pod A: Core State Engine
# ---------------------------------------------------------------------------

def update_state_placeholder(current_state, event_signal):
    new_state = dict(current_state)
    for name, signal in event_signal.items():
        if name not in new_state:
            continue
        speed = VARIABLES[name]["speed"]
        blend = 0.6 if speed == "fast" else 0.15
        suggested = new_state[name] + signal.get("delta", 0)
        low, high = VARIABLES[name]["range"]
        suggested = max(low, min(high, suggested))
        new_state[name] = round(
            new_state[name] * (1 - blend) + suggested * blend, 2
        )
    return new_state


# ---------------------------------------------------------------------------
# PLACEHOLDER — Pod B: Event Understanding
# ---------------------------------------------------------------------------

def interpret_event_placeholder(event_text):
    """
    Fake version of Pod B's function. Outputs the SAME shape as real Pod B
    now: {variable: {"value": 0-10, "confidence": 0-1}} — an absolute
    level, not a delta, so both paths feed the rest of the pipeline
    identically.
    """
    signal = {}
    for name in VARIABLES:
        signal[name] = {
            "value": round(random.uniform(2.0, 8.0), 2),
            "confidence": round(random.uniform(0.4, 0.95), 2),
        }
    return signal


def get_event_signal(event_text):
    """
    Tries Pod B's real analyze_event() first. Falls back to the placeholder
    automatically on ANY failure — missing API key, network issue, rate
    limit, bad output — so the demo never breaks because of Pod B.
    Returns (signal_dict, used_real: bool).
    """
    if POD_B_AVAILABLE:
        try:
            result = _pod_b_analyze_event(event_text)
            # Real Pod B shape: {"signals": {var: {"value","confidence","rationale"}}}
            # Ours needs just: {var: {"value","confidence"}}
            signals = result.get("signals", {})
            signal = {
                var: {"value": data["value"], "confidence": data["confidence"]}
                for var, data in signals.items()
            }
            return signal, True
        except Exception as exc:
            print(f"[Pod B real call failed, using placeholder: {exc}]")
    return interpret_event_placeholder(event_text), False


# ---------------------------------------------------------------------------
# PLACEHOLDER — Pod C: Event Storage
# ---------------------------------------------------------------------------

def _log_to_pod_c(text, signal, timestamp):
    """Best-effort durable log into Pod C's real SQLite store. Any failure
    here is printed as a warning but never raised — our own events.json
    stays the source of truth for query/then/now."""
    if not POD_C_AVAILABLE:
        return
    try:
        # Their schema wants ONE confidence per event; we average across
        # whichever variables this event touched.
        confidences = [sig.get("confidence", 0.5) for sig in signal.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        pod_c_store.add_event(
            description=text,
            happened_at=timestamp,
            change_data=signal,
            confidence=avg_confidence,
        )
    except Exception as exc:
        print(f"[Pod C log failed (non-fatal): {exc}]")


def add_event_placeholder(text, signal, timestamp=None, persist=True,
                           event_list=None):
    event = {
        "text": text,
        "timestamp": (timestamp or datetime.now()).isoformat(),
        "signal": signal,
    }
    target = EVENT_LOG if event_list is None else event_list
    target.append(event)
    if persist:
        save_events(EVENT_LOG)
        _log_to_pod_c(text, signal, event["timestamp"])
    return event


def fetch_events_placeholder(start=None, end=None, event_list=None):
    source = EVENT_LOG if event_list is None else event_list
    if start is None and end is None:
        return list(source)
    result = []
    for e in source:
        ts = datetime.fromisoformat(e["timestamp"])
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        result.append(e)
    return result


# ---------------------------------------------------------------------------
# POD D — Real Backward Smoothing (v0.2, REAL CODE via adapter)
# ---------------------------------------------------------------------------
#
# Pod D's functions expect a different event shape than ours:
#   ours:   {timestamp, text, signal: {var: {delta, confidence}, ...}}
#   theirs: {timestamp, variable, suggested_value, confidence}  (ONE var per event)
#
# This adapter flattens each of our multi-variable events into several
# single-variable events, converting delta -> suggested_value by adding
# the delta to Pod D's own starting value for that variable (5.0, matching
# ours). Pod D's target_date/timestamp comparison is plain string
# comparison, which works correctly for ISO-format datetimes.

def _adapt_events_for_pod_d(our_events):
    adapted = []
    for e in our_events:
        ts = e["timestamp"]
        for var_name, sig in e["signal"].items():
            if var_name not in pod_d_final.STARTING_STATE:
                continue
            adapted.append({
                "timestamp": ts,
                "variable": var_name,
                "suggested_value": sig.get("value", 5.0),
                "confidence": sig.get("confidence", 0.5),
            })
    return adapted


def query_then_placeholder(target_date, event_list=None):
    """Pod D's real get_belief_then, via the adapter."""
    our_events = fetch_events_placeholder(event_list=event_list)
    adapted = _adapt_events_for_pod_d(our_events)
    target_str = target_date.isoformat() if hasattr(target_date, "isoformat") else target_date
    result = pod_d_final.get_belief_then(
        pod_d_final.STARTING_STATE, adapted, target_str
    )
    # Flatten (value, spread) dict down to plain values for existing CLI
    # printing, but keep spread visible too.
    return {var: {"value": round(d["value"], 2), "spread": round(d["spread"], 2)}
            for var, d in result.items()}


def query_now_placeholder(target_date, event_list=None):
    """Pod D's real get_belief_now, via the adapter."""
    our_events = fetch_events_placeholder(event_list=event_list)
    adapted = _adapt_events_for_pod_d(our_events)
    target_str = target_date.isoformat() if hasattr(target_date, "isoformat") else target_date
    result = pod_d_final.get_belief_now(
        pod_d_final.STARTING_STATE, adapted, target_str
    )
    return {var: {"value": round(d["value"], 2), "spread": round(d["spread"], 2)}
            for var, d in result.items()}


# ---------------------------------------------------------------------------
# CLI COMMANDS
# ---------------------------------------------------------------------------

def cmd_add_event(args):
    signal, used_real = get_event_signal(args.text)
    event = add_event_placeholder(args.text, signal)
    source = "Pod B (real)" if used_real else "placeholder"
    print(f"Added event: \"{event['text']}\" at {event['timestamp']} [{source}]")
    print(json.dumps(signal, indent=2))


def cmd_storage_stats(args):
    if not POD_C_AVAILABLE:
        print(f"Pod C storage not available: {_pod_c_import_error_msg}")
        return
    stats = pod_c_store.get_storage_stats()
    print("--- Pod C storage stats (real SQLite checkpoints) ---")
    print(json.dumps(stats, indent=2))


def cmd_query(args):
    try:
        target_date = datetime.fromisoformat(args.date)
    except ValueError:
        print(f"Invalid date format: '{args.date}'. Use YYYY-MM-DD.")
        return

    then_state = query_then_placeholder(target_date)
    now_state = query_now_placeholder(target_date)

    print(f"\n--- What we believed THEN (as of {args.date}) ---")
    print(json.dumps(then_state, indent=2))

    print(f"\n--- What we believe NOW about that same date ---")
    print(json.dumps(now_state, indent=2))


def cmd_demo(args):
    print("=== chronis-ai DEMO ===\n")

    demo_events = []

    scenario = [
        ("felt confident presenting to the team", None),
        ("missed a deadline on the follow-up work", None),
        ("presentation actually went badly and caused ongoing stress",
         None),
    ]

    base_time = datetime(2026, 7, 1)
    reveal_date = None

    for i, (text, _) in enumerate(scenario):
        ts = base_time + timedelta(days=i)
        signal = interpret_event_placeholder(text)
        add_event_placeholder(text, signal, timestamp=ts, persist=False,
                               event_list=demo_events)
        print(f"[Day {i+1}] Event: \"{text}\"")
        if i == 0:
            reveal_date = ts

    print("\n--- Reveal moment: what did we think about Day 1 then vs now? ---")
    then_state = query_then_placeholder(reveal_date, event_list=demo_events)
    now_state = query_now_placeholder(reveal_date, event_list=demo_events)
    print("THEN:", json.dumps(then_state, indent=2))
    print("NOW: ", json.dumps(now_state, indent=2))
    print(
        "\nThe 'now' answer is more trustworthy because it incorporates "
        "later events that revealed the true context behind the early one."
    )


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="chronis",
        description="chronis-ai Personal Memory Assistant CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add-event", help="Add a new event")
    p_add.add_argument("text", help="Plain-text description of the event")
    p_add.set_defaults(func=cmd_add_event)

    p_query = subparsers.add_parser(
        "query", help="Query what the system believed at a given date"
    )
    p_query.add_argument(
        "date", help="Target date, e.g. 2026-07-02 or 2026-07-02T12:00:00"
    )
    p_query.set_defaults(func=cmd_query)

    p_demo = subparsers.add_parser("demo", help="Run the full scripted demo")
    p_demo.set_defaults(func=cmd_demo)

    p_stats = subparsers.add_parser(
        "storage-stats", help="Show Pod C's real checkpoint storage stats"
    )
    p_stats.set_defaults(func=cmd_storage_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
