"""PROCESS module (DEV 2): InputContext -> list[RootCauseCandidate]."""
from __future__ import annotations

from src.process_module.detect import rank_components
from src.process_module.reasoner import generate_candidates
from src.process_module.transform import to_features
from src.schemas import InputContext, RootCauseCandidate


def analyze(ctx: InputContext, top_k: int = 1) -> list[RootCauseCandidate]:
    """Transform telemetry -> detect anomalies -> explain as root-cause candidates."""
    features = to_features(ctx.telemetry)
    ranked = rank_components(features)
    return generate_candidates(ctx, ranked, top_k=top_k)
