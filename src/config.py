"""Central configuration loader with environment-based secret overlays."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_EXAMPLE_QUERY = (
    "On 2021-03-25 between 09:00 and 09:30 the delivery-tracking service "
    "showed elevated errors. Identify the root cause component and reason."
)

_DEFAULTS: dict[str, Any] = {
    "system": "Market",
    "data_root": "./data",
    "use_mock": True,
    "default_date": "2021-03-25",
    "timestamp_offset_hours": 0,
    "top_k": 1,
    "example_query": DEFAULT_EXAMPLE_QUERY,
    "llm": {
        "source": "Gemini",
        "model": "gemini-3.5-flash-lite",
        "api_key_env": "GEMINI_API_KEY",
    },
}


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping, falling back to defaults when it is unavailable."""
    try:
        import yaml

        with path.open("r", encoding="utf-8") as config_file:
            loaded = yaml.safe_load(config_file) or {}
    except (ImportError, OSError):
        return {}

    if not isinstance(loaded, dict):
        raise ValueError(f"Configuration must be a YAML mapping: {path}")
    return loaded


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load YAML settings and overlay credentials from environment variables.

    Non-secret LLM fields from YAML (for example ``source`` and
    ``api_key_env``) are preserved. The API key itself is only read from the
    environment variable named by ``api_key_env``.
    """
    load_dotenv(ROOT_DIR / ".env")

    config: dict[str, Any] = dict(_DEFAULTS)
    config["llm"] = dict(_DEFAULTS["llm"])

    config_path = Path(path) if path is not None else ROOT_DIR / "config" / "config.yaml"
    if path is not None and not config_path.is_file():
        raise FileNotFoundError(f"Explicit configuration file not found: {config_path}")
    yaml_config = _load_yaml(config_path)
    yaml_llm = yaml_config.pop("llm", None)
    config.update(yaml_config)

    if yaml_llm is not None:
        if not isinstance(yaml_llm, dict):
            raise ValueError("The 'llm' configuration must be a mapping")
        config["llm"].update(yaml_llm)

    config["database"] = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "openrca"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
    }
    config["jira"] = {
        "url": os.getenv("JIRA_URL", ""),
        "email": os.getenv("JIRA_EMAIL", ""),
        "token": os.getenv("JIRA_API_TOKEN", ""),
        "project_key": os.getenv("JIRA_PROJECT_KEY", ""),
    }

    llm_config = config["llm"]
    if model_override := os.getenv("GEMINI_MODEL"):
        llm_config["model"] = model_override
    api_key_env = str(llm_config.get("api_key_env", "GEMINI_API_KEY"))
    llm_config["api_key_env"] = api_key_env
    llm_config["api_key"] = os.getenv(api_key_env, "")

    return config
