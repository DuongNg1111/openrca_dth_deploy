"""OpenRCA-style scoring of predictions vs ground truth.

A prediction is "correct" if the predicted component matches ground truth
(optionally also checking the reason). Returns an accuracy summary.
"""
from __future__ import annotations


def score_one(pred: dict, truth: dict, check_reason: bool = False) -> bool:
    comp_ok = pred.get("root cause component") == truth.get("root cause component")
    if not check_reason:
        return comp_ok
    truth_reason = (truth.get("root cause reason") or "").lower()
    pred_reason = (pred.get("root cause reason") or "").lower()
    return comp_ok and truth_reason in pred_reason


def score(predictions: list[dict], truths: list[dict], check_reason: bool = False) -> dict:
    """Return {"n", "correct", "accuracy"} over aligned prediction/truth lists."""
    n = min(len(predictions), len(truths))
    hits = sum(score_one(predictions[i], truths[i], check_reason) for i in range(n))
    return {"n": n, "correct": hits, "accuracy": (hits / n if n else 0.0)}
