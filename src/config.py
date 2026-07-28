"""Tiny config loader. Works even without PyYAML installed (falls back to defaults)."""
from __future__ import annotations

import os

_DEFAULTS = {
    "system": "Market",
    "data_root": "/home/ubuntu/Market",
    "use_mock": True,
    "default_date": "2021-03-25",
    "top_k": 1,
    "example_query": "On 2021-03-25 between 09:00 and 09:30 the delivery-tracking service showed elevated errors. Identify the root cause component and the root cause reason.",
    "llm": {"source": "OpenAI", "model": "gpt-4o", "api_key_env": "OPENAI_API_KEY"},
}


def load_config(path: str | None = None) -> dict:
    """Load config/config.yaml, or return sensible defaults if PyYAML/file missing."""
    cfg = dict(_DEFAULTS)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    try:
        import yaml  # type: ignore

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        cfg.update(data)
    except Exception:
        pass  # PyYAML not installed or file absent -> defaults (fine for the smoke test)
    return cfg
