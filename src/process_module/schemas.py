"""Data contracts used by the process module's evidence validation step."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ValidationStatus = Literal["COMPLETE", "INCOMPLETE", "FAILED"]


@dataclass(frozen=True)
class ValidationResult:
    """Result of checking whether evidence is ready for RCA reasoning."""

    status: ValidationStatus
    confidence: float
    reason: str
    missing_evidence: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    ready_for_reasoning: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.ready_for_reasoning != (self.status == "COMPLETE"):
            raise ValueError(
                "ready_for_reasoning must be true exactly when status is COMPLETE"
            )
