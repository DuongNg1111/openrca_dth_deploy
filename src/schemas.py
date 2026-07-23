"""Shared data contracts between the three pipeline modules.

These dataclasses are the *interface* between DEV 1 (input), DEV 2 (process) and
DEV 3 (output). Agree on these shapes first, then each dev works independently.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TimeWindow:
    start: datetime
    end: datetime

    def contains(self, ts: datetime) -> bool:
        return self.start <= ts <= self.end


@dataclass
class InputContext:
    """Produced by the INPUT module, consumed by the PROCESS module."""

    raw_query: str
    system: str
    time_window: TimeWindow
    components_hint: list[str] = field(default_factory=list)
    telemetry: dict[str, Any] = field(default_factory=dict)


@dataclass
class RootCauseCandidate:
    """Produced by the PROCESS module, consumed by the OUTPUT module."""

    component: str
    reason: str
    occurrence_time: datetime
    confidence: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class Prediction:
    """Final result built by the OUTPUT module."""

    candidates: list[RootCauseCandidate] = field(default_factory=list)

    def to_openrca_json(self) -> dict[str, dict[str, str]]:
        """Serialize to OpenRCA's expected prediction format."""
        out: dict[str, dict[str, str]] = {}
        for i, c in enumerate(self.candidates, start=1):
            out[str(i)] = {
                "root cause occurrence datetime": c.occurrence_time.strftime("%Y-%m-%d %H:%M:%S"),
                "root cause component": c.component,
                "root cause reason": c.reason,
            }
        return out

@dataclass
class RawQuery:
    issue_key: str

    incident_description: str
    additional_information: str
    
    environment: str
    affected_system: str
    incident_time: str

    reporter: str
    status: str
    created: str

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)

@dataclass
class ParsedQuery:
    issue_key: str
    environment: str
    incident_description: str
    affected_system: str
    incident_time: datetime | str
    additional_information: str

    keywords: list[str] = field(default_factory=list)