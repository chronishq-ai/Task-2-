from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import ValidationError

from config import settings
from llm_client import LLMProvider, get_provider
from logger import EventLogger
from prompt import build_prompt
from schemas import EventSignals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pod_b.analyzer")

_event_logger = EventLogger(settings.log_path)
_provider: Optional[LLMProvider] = None


def _get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = get_provider(settings)
    return _provider


def set_provider(provider: LLMProvider) -> None:
    global _provider
    _provider = provider


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _parse_and_validate(raw: str) -> EventSignals:
    cleaned = _strip_markdown_fences(raw)
    data = json.loads(cleaned)
    return EventSignals(**data)


def analyze_event(event: str, max_retries: Optional[int] = None) -> dict:
    provider = _get_provider()
    retries = settings.max_retries if max_retries is None else max_retries
    prompt = build_prompt(event)
    last_error: Optional[str] = None
    raw_response = ""

    for attempt in range(1, retries + 1):
        try:
            raw_response = provider.generate(prompt)
            result = _parse_and_validate(raw_response)
            payload = result.model_dump()
            _event_logger.log(event, raw_response, payload)
            return payload
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = str(exc)
            logger.warning("invalid output attempt %d/%d: %s", attempt, retries, last_error)
            prompt = (
                build_prompt(event)
                + f"\n\nYour previous response was invalid ({last_error}). "
                  "Return ONLY valid JSON matching the schema, with no extra text."
            )
        except Exception as exc:
            last_error = str(exc)
            logger.error("provider error attempt %d/%d: %s", attempt, retries, last_error)

    _event_logger.log(event, raw_response, None, error=last_error)
    raise RuntimeError(f"Failed to get valid signals after {retries} attempts: {last_error}")
