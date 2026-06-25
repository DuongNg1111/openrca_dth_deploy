"""PROCESS module — turn ranked anomalies into RootCauseCandidate objects."""
from __future__ import annotations

from src.schemas import RootCauseCandidate

KPI_TO_REASON = {'disk_io_read': 'high disk I/O read usage', 'cpu': 'CPU saturation', 'memory': 'memory exhaustion', 'latency': 'elevated request latency'}


def explain(kpi: str) -> str:
    """Map an anomalous KPI to a human-readable reason."""
    return KPI_TO_REASON.get(kpi, f"anomalous {kpi}")


def generate_candidates(ctx, ranked, top_k: int = 1):
    """Map the top anomalies to root-cause candidates.

    TODO(DEV 2): optionally call an LLM to write a richer `reason` using the
    surrounding logs/traces as evidence (this is a strong place to add novelty).
    """
    out = []
    seen = set()
    occ = ctx.time_window.end
    for s in ranked:
        if s["component"] in seen:
            continue
        seen.add(s["component"])
        conf = max(0.0, min(1.0, s["score"] / 50.0))
        out.append(
            RootCauseCandidate(
                component=s["component"],
                reason=explain(s["kpi"]),
                occurrence_time=occ,
                confidence=round(conf, 3),
                evidence={"kpi": s["kpi"], "z_score": round(s["score"], 2), "peak": s["peak"]},
            )
        )
        if len(out) >= top_k:
            break
    return out
