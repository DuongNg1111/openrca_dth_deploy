"""PROCESS module — anomaly detection over features -> ranked components.


"""
from __future__ import annotations

from statistics import mean, pstdev


def anomaly_scores(features, baseline_frac: float = 0.66):
    """Change-point style score: how far the recent window deviates from the baseline.

    score = (max(recent) - mean(baseline)) / std(baseline), per (component, kpi).
    """
    scores = []
    for (comp, kpi), f in features.items():
        vals = f["values"]
        k = max(1, int(len(vals) * baseline_frac))
        baseline = vals[:k]
        recent = vals[k:] or vals[-1:]
        mu = mean(baseline)
        sd = pstdev(baseline) or 1e-9
        scores.append(
            {"component": comp, "kpi": kpi, "score": (max(recent) - mu) / sd, "peak": max(recent)}
        )
    scores.sort(key=lambda s: s["score"], reverse=True)
    return scores


def rank_components(features):
    """Most anomalous (component, kpi) first. TODO(DEV 2): try better detectors."""
    return anomaly_scores(features)
