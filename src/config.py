"""Central configuration loader."""
from __future__ import annotations
import os
from pathlib import Path


_DEFAULTS = {

    "system": "Market",

    "data_root": os.getenv(
        "OPENRCA_DATA_ROOT",
        "/home/ubuntu/Market"
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

        "password_env": "POSTGRES_PASSWORD"
    },


    "jira": {

        "project_key": "DEV",

        "url_env": "JIRA_URL",

        "email_env": "JIRA_EMAIL",

        "token_env": "JIRA_API_TOKEN"
    },


    "llm": {

        "source": "Gemini",

        "model": "gemini-2.5-pro",

        "api_key_env": "GEMINI_API_KEY"
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