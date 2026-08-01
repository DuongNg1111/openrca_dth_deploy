"""Central configuration loader."""
from __future__ import annotations
import os
from pathlib import Path

_DEFAULTS = {
    "system": "Market",
    # Ép buộc data_root trỏ chuẩn xác về thư mục Market trên máy Mac của bạn bất kể config.yaml có ghi gì
    "data_root": str(Path(__file__).resolve().parent.parent/"data"/ "Market"),

    "database": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB", "openrca"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
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
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY"
    },
    "top_k": 1,
    "use_mock": False,
}

def load_config(path: str | None = None) -> dict:
    cfg = dict(_DEFAULTS)
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "config.yaml"
        )
    try:
        import yaml  # type: ignore
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        cfg.update(data)
    except Exception:
        pass

    # An toàn tuyệt đối: nếu data_root trong file yaml/default đang là dạng tương đối, tự động chuyển thành tuyệt đối
    if not os.path.isabs(cfg["data_root"]) or cfg["data_root"] == "data":
        cfg["data_root"] = str(Path(__file__).resolve().parent.parent /"data"/ "Market")

    return cfg