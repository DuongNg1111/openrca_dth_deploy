"""Smoke test — runs without the real dataset (mock telemetry).

pytest:      python -m pytest -q
standalone:  python tests/test_pipeline_smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import load_config
from src.pipeline import run
from src.schemas import Prediction


def test_pipeline_runs_and_returns_prediction():
    cfg = load_config()
    pred = run(cfg["example_query"], cfg)
    assert isinstance(pred, Prediction)
    assert len(pred.candidates) >= 1
    first = pred.to_openrca_json()["1"]
    assert set(first) == {
        "root cause occurrence datetime",
        "root cause component",
        "root cause reason",
    }
    assert first["root cause component"]


def test_pipeline_finds_injected_root_cause():
    cfg = load_config()
    pred = run(cfg["example_query"], cfg)
    assert pred.candidates[0].component == "order-service"


if __name__ == "__main__":
    test_pipeline_runs_and_returns_prediction()
    test_pipeline_finds_injected_root_cause()
    print("OK: smoke tests passed")
