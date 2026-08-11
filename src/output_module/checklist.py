"""
OUTPUT module — Evidence Validation Checklist.

This module validates the Root Cause Candidate produced by the
Process Module before generating the final RCA report.

Author: DEV3 (Output)
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ==========================================================
# Configuration
# ==========================================================

MAX_RETRY = 3

CONFIDENCE_THRESHOLD = 0.80

MIN_CHECK_SCORE = 5

TOTAL_CHECKS = 6


# ==========================================================
# Checklist Result
# ==========================================================

@dataclass
class ChecklistResult:

    status: str

    score: int

    max_score: int

    retry_required: bool

    failed_checks: list[str] = field(default_factory=list)

    recommendation: str = ""


# ==========================================================
# Individual Checks
# ==========================================================

def check_metric(candidate) -> bool:
    """
    Metric evidence exists.
    """
    return len(candidate.evidence.get("metrics", [])) > 0


def check_log(candidate) -> bool:
    """
    Log evidence exists.
    """
    return len(candidate.evidence.get("logs", [])) > 0


def check_trace(candidate) -> bool:
    """
    Trace evidence exists.
    """
    return len(candidate.evidence.get("traces", [])) > 0


def check_confidence(candidate) -> bool:
    """
    Confidence must be above threshold.
    """
    return candidate.confidence >= CONFIDENCE_THRESHOLD


def check_reason(candidate) -> bool:
    """
    Root cause explanation must exist.
    """
    return candidate.reason is not None and candidate.reason.strip() != ""


def check_component(candidate) -> bool:
    """
    Component must exist.
    """
    return candidate.component is not None and candidate.component.strip() != ""


# ==========================================================
# Main Evaluation
# ==========================================================

def evaluate_candidate(candidate) -> ChecklistResult:
    """
    Evaluate whether the Root Cause Candidate is reliable.
    """

    score = 0

    failed = []

    if check_metric(candidate):
        score += 1
    else:
        failed.append("Metric Validation")

    if check_log(candidate):
        score += 1
    else:
        failed.append("Log Validation")

    if check_trace(candidate):
        score += 1
    else:
        failed.append("Trace Validation")

    if check_confidence(candidate):
        score += 1
    else:
        failed.append("Confidence Check")

    if check_reason(candidate):
        score += 1
    else:
        failed.append("Reason Check")

    if check_component(candidate):
        score += 1
    else:
        failed.append("Component Check")

    # ----------------------------------------
    # Final Decision
    # ----------------------------------------

    if score == TOTAL_CHECKS:

        return ChecklistResult(
            status="CONFIRMED",
            score=score,
            max_score=TOTAL_CHECKS,
            retry_required=False,
            failed_checks=[],
            recommendation="Ready to generate RCA report."
        )

    if score >= MIN_CHECK_SCORE:

        return ChecklistResult(
            status="RETRY_REQUIRED",
            score=score,
            max_score=TOTAL_CHECKS,
            retry_required=True,
            failed_checks=failed,
            recommendation=(
                "Evidence is partially sufficient. "
                "Retrieve additional telemetry and run "
                "Reasoning Agent again."
            )
        )

    return ChecklistResult(
        status="UNRESOLVED",
        score=score,
        max_score=TOTAL_CHECKS,
        retry_required=False,
        failed_checks=failed,
        recommendation=(
            "Unable to determine the root cause. "
            "Evidence is insufficient."
        )
    )


# ==========================================================
# Retry Controller
# ==========================================================

def should_retry(result: ChecklistResult, retry_count: int) -> bool:
    """
    Decide whether the pipeline should request another
    reasoning iteration.
    """

    return (
        result.retry_required
        and retry_count < MAX_RETRY
    )


# ==========================================================
# Batch Evaluation
# ==========================================================

def evaluate_prediction(prediction):
    """
    Evaluate all Root Cause Candidates.
    """

    results = []

    for candidate in prediction.candidates:

        results.append(
            evaluate_candidate(candidate)
        )

    return results