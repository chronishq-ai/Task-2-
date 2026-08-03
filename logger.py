"""
Append-only JSON logging of every request/response pair, as required by
the Pod B spec ("Save every request and response into a log file").
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Optional

_lock = threading.Lock()


class EventLogger:
    def __init__(self, log_path: str):
        self._path = log_path
        directory = os.path.dirname(self._path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self._path):
            with open(self._path, "w") as f:
                json.dump([], f)

    def log(
        self,
        event: str,
        raw_response: str,
        parsed: Optional[dict],
        error: Optional[str] = None,
    ) -> None:
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "raw_response": raw_response,
            "parsed": parsed,
            "error": error,
        }
class EvaluationLogger:
    """
    v0.2 addition - append-only log of per (event, variable) evaluation
    records: human rating, baseline prediction, LLM prediction, and the
    resulting metric value. Separate from EventLogger/its file on purpose:
    EventLogger's log() signature and file stay untouched (analyzer.py
    depends on it exactly as it was in v0.1), this is new data alongside
    it, not a replacement.

    Same append-only, read-modify-write-under-lock pattern as EventLogger,
    including failed pairs - per spec section 7, failed examples must be
    saved too, not silently dropped.
    """

    def __init__(self, log_path: str = "logs/evaluation_details.json"):
        self._path = log_path
        directory = os.path.dirname(self._path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self._path):
            with open(self._path, "w") as f:
                json.dump([], f)

    def log(
        self,
        event_id: str,
        variable: str,
        human_rating: Optional[float],
        baseline_prediction: Optional[float],
        llm_prediction: Optional[float],
        metric_value: Optional[float],
        error: Optional[str] = None,
    ) -> None:
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": event_id,
            "variable": variable,
            "human_rating": human_rating,
            "baseline_prediction": baseline_prediction,
            "llm_prediction": llm_prediction,
            "metric_value": metric_value,
            "error": error,
        }
        with _lock:
            with open(self._path, "r+") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()