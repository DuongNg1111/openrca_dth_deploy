"""OUTPUT module — build and export RCA prediction results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.schemas import Prediction, RootCauseCandidate


def aggregate_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    """
    Aggregate evidence returned by different AI agents.

    Expected keys:
        - metrics
        - logs
        - traces

    Missing keys will be replaced with empty lists.
    """

    return {
    "metrics": candidate.get("metrics", []),
    "logs": candidate.get("logs", []),
    "traces": candidate.get("traces", []),

    # Optional fields from Process Module
    "status": candidate.get("evidence_status", "UNKNOWN"),
    "missing": candidate.get("missing_evidence", []),
    "explanation": candidate.get("explanation", ""),
}


def build_output(candidates: list[dict[str, Any]]) -> Prediction:
    """
    Convert reasoning results into a Prediction object.

    Parameters
    ----------
    candidates
        Output produced by the Process Module.

    Returns
    -------
    Prediction
    """

    prediction = Prediction()

    for item in candidates:

        rc = RootCauseCandidate(
            component=item["component"],
            reason=item["reason"],
            occurrence_time=item["occurrence_time"],
            confidence=item.get("confidence", 0.0),
            evidence=aggregate_evidence(item),
        )

        prediction.candidates.append(rc)

    return prediction


def save_prediction(prediction: Prediction, path: str | Path):
    """
    Save Prediction as an OpenRCA JSON file.
    """

    path = Path(path)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            prediction.to_openrca_json(),
            f,
            indent=4,
            ensure_ascii=False,
        )


def build_dashboard_data(prediction: Prediction) -> dict[str, Any]:
    """
    Convert Prediction into dashboard-friendly data.

    This output is intended for the Streamlit frontend.
    """

    candidates = []

    for c in prediction.candidates:

        candidates.append(
            {
                "component": c.component,
                "reason": c.reason,
                "confidence": round(c.confidence, 3),
                "occurrence_time": c.occurrence_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "metrics": len(c.evidence.get("metrics", [])),
                "logs": len(c.evidence.get("logs", [])),
                "traces": len(c.evidence.get("traces", [])),

                "evidence_status": c.evidence.get(
                    "status",
                    "UNKNOWN",
                ),

                "missing_evidence": c.evidence.get(
                    "missing",
                    [],
                ),

                "explanation": c.evidence.get(
                    "explanation",
                    "",
                ),

                "evidence": c.evidence,
            }
        )

    highest = None

    if candidates:
        highest = max(
            candidates,
            key=lambda x: x["confidence"],
        )

    return {
        "total_candidates": len(candidates),
        "highest_confidence": (
            highest["confidence"] if highest else 0
        ),
        "top_component": (
            highest["component"] if highest else None
        ),
        "top_reason": (
            highest["reason"] if highest else None
        ),
        "candidates": candidates,
    }
def build_summary(prediction: Prediction) -> dict[str, Any]:
    """
    Generate a compact summary for the dashboard.
    """

    if not prediction.candidates:

        return {
            "total_candidates": 0,
            "top_component": None,
            "top_reason": None,
            "highest_confidence": 0,
        }

    best = max(
        prediction.candidates,
        key=lambda x: x.confidence,
    )

    return {
        "total_candidates": len(prediction.candidates),
        "top_component": best.component,
        "top_reason": best.reason,
        "highest_confidence": round(best.confidence, 3),
    }