from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_VARIABLES = {
    "mood",
    "focus",
    "stress",
    "confidence",
    "trust",
    "motivation",
    "social_engagement",
}


class Signal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float = Field(..., ge=0, le=10, description="Estimated level, 0-10")
    confidence: float = Field(..., ge=0, le=1, description="Model's confidence, 0-1")
    rationale: Optional[str] = Field(default=None)


class EventSignals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signals: Dict[str, Signal]

    @field_validator("signals")
    @classmethod
    def validate_keys(cls, v: Dict[str, Signal]) -> Dict[str, Signal]:
        unknown = {k for k in v.keys() if k.lower() not in VALID_VARIABLES}
        if unknown:
            raise ValueError(f"Unknown variable keys in signals: {sorted(unknown)}")
        return {k.lower(): val for k, val in v.items()}
