"""PROCESS module — clean & aggregate telemetry into per-(component,kpi) series."""
from __future__ import annotations


def aggregate_metrics(metric_rows):
    """Group metric rows by (component, kpi) -> time-ordered list of values."""
    groups: dict = {}
    for r in metric_rows:
        groups.setdefault((r["component"], r["kpi"]), []).append(r["value"])
    return groups


def to_features(telemetry) -> dict:
    """Return {(component, kpi): {"values": [...], "n": int}} (values stay time-ordered)."""
    groups = aggregate_metrics(telemetry.get("metric", []))
    return {key: {"values": vals, "n": len(vals)} for key, vals in groups.items()}
