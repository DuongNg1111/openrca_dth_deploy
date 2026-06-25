"""OUTPUT module — assemble & save the final OpenRCA-format prediction."""
from __future__ import annotations

import json

from src.schemas import Prediction


def build_prediction(candidates) -> Prediction:
    return Prediction(candidates=list(candidates))


def save_prediction(pred: Prediction, path: str) -> None:
    """Write the prediction JSON to `path` (OpenRCA format)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pred.to_openrca_json(), f, indent=2, ensure_ascii=False)
