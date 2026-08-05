"""Central configuration loader."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# =====================================================
# Load .env
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    ROOT_DIR / ".env"
)


# =====================================================
# Load configuration
# =====================================================

def load_config():

    config = {}


    # ---------------------------------------------
    # Load project config.yaml
    # ---------------------------------------------

    config_path = (
        ROOT_DIR
        / "config"
        / "config.yaml"
    )

    try:

        import yaml

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as f:

            config = yaml.safe_load(f) or {}

    except Exception:

        config = {}


    # ---------------------------------------------
    # Database (from .env)
    # ---------------------------------------------

    config["database"] = {

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

    }


    # ---------------------------------------------
    # Jira (from .env)
    # ---------------------------------------------

    config["jira"] = {

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

    "project_key": os.getenv(
        "JIRA_PROJECT_KEY",
        ""
    ),

}


    # ---------------------------------------------
    # Gemini (from .env)
    # ---------------------------------------------

    config["llm"] = {

        "model": os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash"
        ),

        "api_key": os.getenv(
            "GEMINI_API_KEY",
            ""
        ),

    }


    # ---------------------------------------------
    # Default values
    # ---------------------------------------------

    config.setdefault(
        "system",
        "Market"
    )

    config.setdefault(
        "data_root",
        "./data"
    )

    config.setdefault(
        "use_mock",
        False
    )

    config.setdefault(
        "top_k",
        1
    )


    return config