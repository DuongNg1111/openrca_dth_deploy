"""OUTPUT module (DEV 3): candidates -> Prediction (+ optional report/plots)."""
from __future__ import annotations

from src.output_module.formatter import build_prediction, save_prediction
from src.output_module.visualize import render_report
from src.schemas import Prediction

__all__ = ["build_output", "save_prediction", "render_report"]


def build_output(candidates) -> Prediction:
    """Assemble the final OpenRCA-format Prediction."""
    return build_prediction(candidates)
