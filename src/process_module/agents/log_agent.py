from __future__ import annotations

import json

from google.genai import types

from src.database.repository import get_investigation_logs
from src.process_module.agents.base_agent import BaseAgent


class LogAgent(BaseAgent):

    def __init__(self, config=None):
        super().__init__("Log Agent", config=config)

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

        error_df = logs_df[
            error_mask
        ].copy()

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

            raw_logs.append(
                {
                "service": service,

                "message": message,

                "count": int(count),

                "first_seen": str(
                    error_df[
                    error_df[message_column]==message
                    ]["timestamp"]
                    .min()
                ),

                "last_seen": str(
                    error_df[
                    error_df[message_column]==message
                    ]["timestamp"]
                    .max()
                )

                }
                )

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

            text = response.text.strip()

            print("\n========== LOG RESPONSE ==========")
            print(text)
            print("===================================")

            result = json.loads(text)
            if not isinstance(result, dict):
                raise ValueError("Log Agent response must be a JSON object")
            return result

        # =====================================================
        # 11. FALLBACK
        # =====================================================

        except Exception:

            fallback_logs = []

            for item in raw_logs:

                fallback_logs.append(
                    {
                        "service": service,
                        "timestamp": timestamp,
                        "level": "ERROR",
                        "error_type": "Unknown",
                        "message": item["message"],
                        "count": item["count"]
                    }
                )

            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "logs": fallback_logs,
                "summary": (
                    f"Detected {len(error_df)} error logs "
                    f"for service '{service}'."
                ),
                "confidence": 0.5
            }
