"""Central configuration loader."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

except ImportError:
    pass


_DEFAULTS = {

    "system": "Market",

    "data_root": os.getenv(
        "OPENRCA_DATA_ROOT",
        "./data"
    ),

    "database": {

        "host": os.getenv(
            "POSTGRES_HOST",
            "localhost"
        ),

        "port": int(
            os.getenv(
                "POSTGRES_PORT",
                5432
            )
        ),

        "database": os.getenv(
            "POSTGRES_DB",
            "openrca"
        ),

        "user": os.getenv(
            "POSTGRES_USER",
            "postgres"
        ),

        "password": os.getenv(
            "POSTGRES_PASSWORD",
            ""
        ),

    },

    "jira": {

        "project_key": "DEV",

        "url": os.getenv(
            "JIRA_URL",
            ""
        ),

        "email": os.getenv(
            "JIRA_EMAIL",
            ""
        ),

        "token": os.getenv(
            "JIRA_API_TOKEN",
            ""
        ),

    },

    "llm": {

        "model": os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash"
        ),

        "api_key": os.getenv(
            "GEMINI_API_KEY",
            ""
        ),

    },

    "top_k": 1,

    "use_mock": False,

}


def load_config(path: str | None = None):

    cfg = dict(_DEFAULTS)

    if path is None:

        path = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            "config",
            "config.yaml"
        )

    try:

        import yaml

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            data = yaml.safe_load(f) or {}

        cfg.update(data)

    except Exception:

        pass

    return cfg