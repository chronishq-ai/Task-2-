from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    anthropic_api_key: Optional[str]
    anthropic_model: str
    groq_api_key: Optional[str]
    groq_model: str
    active_provider: str  # "gemini" | "anthropic" | "groq"
    max_retries: int
    log_path: str


def load_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
gemini_model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        active_provider=os.getenv("LLM_PROVIDER", "gemini").lower(),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        log_path=os.getenv("LOG_PATH", "logs/outputs.json"),
    )


settings = load_settings()