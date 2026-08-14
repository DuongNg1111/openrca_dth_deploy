from __future__ import annotations

import json

from google import genai
from google.genai import types

from src.config import load_config
from src.database.repository import get_investigation_logs
from src.process_module.agents.base_agent import BaseAgent


class LogAgent(BaseAgent):

    def __init__(self, config=None):
        super().__init__("Log Agent", config=config)

        # Load cấu hình từ config.py
        # config.py đã chịu trách nhiệm đọc .env và config.yaml
        self.config = config if config is not None else load_config()

        llm_cfg = self.config.get("llm", {})

        # Lấy API key và model từ config trung tâm
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get("model")

        # Khởi tạo Gemini client
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def analyze(self, context) -> dict:

        investigation_id = getattr(
            context,
            "investigation_id",
            None
        )

        service = getattr(
            context,
            "service",
            "unknown"
        )

        incident_time = getattr(
            context,
            "incident_time",
            ""
        )

        # =====================================================
        # 1. VALIDATE
        # =====================================================

        if investigation_id is None:
            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "logs": [],
                "summary": "Missing investigation_id.",
                "confidence": 0.0
            }

        # =====================================================
        # 2. LOAD LOGS FROM DATABASE
        # =====================================================

        try:
            logs_df = get_investigation_logs(
                investigation_id,
                service=service
            )

        except Exception as e:
            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "logs": [],
                "summary": f"Failed loading logs: {str(e)}",
                "confidence": 0.0
            }

        # =====================================================
        # 3. CHECK EMPTY
        # =====================================================

        if logs_df is None or logs_df.empty:
            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "logs": [],
                "summary": (
                    f"No log data found for service '{service}'."
                ),
                "confidence": 1.0
            }

        # =====================================================
        # 4. FIND MESSAGE COLUMN
        # =====================================================

        message_column = None

        for column in [
            "value",
            "content",
            "message",
            "log",
            "body",
            "text"
        ]:
            if column in logs_df.columns:
                message_column = column
                break

        if message_column is None:
            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "logs": [],
                "summary": "No log message column found.",
                "confidence": 0.5
            }

        # =====================================================
        # 5. DETECT ERROR LOGS
        # =====================================================

        error_pattern = (
            r"error|exception|timeout|"
            r"failed|failure|fatal|"
            r"critical|unavailable|"
            r"refused|reset|"
            r"retry|deadline|"
            r"slow|latency|"
            r"throttle"
        )

        error_mask = (
            logs_df[message_column]
            .astype(str)
            .str.contains(
                error_pattern,
                case=False,
                regex=True,
                na=False
            )
        )

        error_df = logs_df[error_mask].copy()

        # =====================================================
        # 6. NO ERROR
        # =====================================================

        if error_df.empty:
            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "logs": [],
                "summary": (
                    f"No explicit error logs found "
                    f"for service '{service}'."
                ),
                "confidence": 1.0
            }

        # =====================================================
        # 7. GROUP ERROR MESSAGES
        # =====================================================

        grouped = (
            error_df[message_column]
            .astype(str)
            .value_counts()
            .head(10)
        )

        raw_logs = []

        for message, count in grouped.items():

            matching_rows = error_df[
                error_df[message_column].astype(str) == str(message)
            ]

            first_seen = ""
            last_seen = ""

            if "timestamp" in matching_rows.columns:
                first_seen = str(
                    matching_rows["timestamp"].min()
                )
                last_seen = str(
                    matching_rows["timestamp"].max()
                )

            raw_logs.append(
                {
                    "service": service,
                    "message": str(message),
                    "count": int(count),
                    "first_seen": first_seen,
                    "last_seen": last_seen
                }
            )

        # Total number of detected error entries
        total_errors = int(error_df.shape[0])

        # =====================================================
        # 8. TIMESTAMP
        # =====================================================

        timestamp = ""

        if "timestamp" in error_df.columns:
            timestamp = str(
                error_df.iloc[0]["timestamp"]
            )

        # =====================================================
        # 9. GEMINI PROMPT
        # =====================================================

        prompt = f"""
You are an SRE Log Analysis Expert.

Analyze ONLY the supplied log evidence.

Investigation ID:
{investigation_id}

Service:
{service}

Incident Time:
{incident_time}

Grouped Error Evidence:

{json.dumps(
    raw_logs,
    indent=2,
    default=str
)}

Rules:

1. Use ONLY supplied evidence.
2. Do NOT invent error messages.
3. Do NOT invent timestamps.
4. Do NOT invent services.
5. Group repeated errors together.
6. Count must represent occurrences.
7. Return ONLY valid JSON.

Required format:

{{
    "agent": "Log Agent",
    "evidence_type": "log",
    "logs": [
        {{
            "service": "{service}",
            "timestamp": "{timestamp}",
            "level": "ERROR",
            "error_type": "",
            "message": "",
            "count": 0
        }}
    ],
    "summary": "",
    "confidence": 0.0
}}
"""

        # =====================================================
        # 10. CALL GEMINI
        # =====================================================

        try:

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )

            # =================================================
            # 11. PARSE GEMINI RESPONSE
            # =================================================

            response_text = getattr(
                response,
                "text",
                None
            )

            if not response_text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            result = json.loads(response_text)

            # Ensure required fields exist
            result.setdefault("agent", "Log Agent")
            result.setdefault("evidence_type", "log")
            result.setdefault("logs", [])
            result.setdefault("summary", "")
            result.setdefault("confidence", 0.0)

            return result

        except Exception as e:

            # =================================================
            # 12. FALLBACK
            # =================================================

            summary_text = (
                f"Detected {total_errors} raw error entries. "
                f"Gemini analysis unavailable: {str(e)}"
            )

            fallback_errors = [
                {
                    "service": service,
                    "timestamp": timestamp or incident_time,
                    "level": "ERROR",
                    "error_type": "LogAnalysisError",
                    "message": (
                        f"Detected {total_errors} raw error entries. "
                        "Gemini analysis unavailable."
                    ),
                    "count": total_errors
                }
            ]

            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "logs": fallback_errors,
                "summary": summary_text,
                "confidence": 0.5
            }