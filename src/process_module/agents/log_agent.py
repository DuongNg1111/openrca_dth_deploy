from __future__ import annotations

import json

from google import genai
from google.genai import types

from src.process_module.agents.base_agent import BaseAgent
from src.database.repository import get_investigation_logs


class LogAgent(BaseAgent):

    def __init__(self):
        super().__init__("Log Agent")

    def analyze(self, context) -> dict:
        """
        Analyze logs stored in PostgreSQL for one investigation
        and one logical service.

        Flow:

            investigation_logs
                    ↓
            query by investigation_id + service
                    ↓
            LogAgent
                    ↓
            detect error-related logs
                    ↓
            Gemini analysis
                    ↓
            structured log evidence
                    ↓
            full_pipeline
                    ↓
            evidence_records
        """

        # =====================================================
        # 1. GET CONTEXT INFORMATION
        # =====================================================

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
        # 2. VALIDATE INVESTIGATION ID
        # =====================================================

        if investigation_id is None:

            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "errors": [],
                "summary": (
                    "Log analysis skipped because "
                    "investigation_id was not provided."
                ),
                "confidence": 0.0,
            }

        # =====================================================
        # 3. LOAD LOG DATA FROM DATABASE
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
                "errors": [],
                "summary": (
                    f"Unable to load logs for "
                    f"investigation {investigation_id}: "
                    f"{str(e)}"
                ),
                "confidence": 0.0,
            }

        # =====================================================
        # 4. VALIDATE DATA
        # =====================================================

        if logs_df is None or logs_df.empty:

            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "errors": [],
                "summary": (
                    f"No log data found for service "
                    f"'{service}' in investigation "
                    f"{investigation_id}."
                ),
                "confidence": 1.0,
            }

        # =====================================================
        # 5. FIND LOG CONTENT COLUMN
        # =====================================================

        content_column = None

        for candidate in [
            "value",
            "content",
            "message",
            "log",
            "body",
            "text",
        ]:

            if candidate in logs_df.columns:

                content_column = candidate
                break

        if content_column is None:

            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "errors": [],
                "summary": (
                    f"No usable log content column found "
                    f"for service '{service}'."
                ),
                "confidence": 0.5,
            }

        # =====================================================
        # 6. FIND ERROR LOGS
        # =====================================================

        error_pattern = (
            r"error|exception|timeout|fail|failed|failure|"
            r"fatal|critical|slow|unavailable"
        )

        error_mask = (
            logs_df[content_column]
            .astype(str)
            .str.contains(
                error_pattern,
                case=False,
                na=False,
                regex=True,
            )
        )

        error_df = logs_df[
            error_mask
        ].copy()

        error_count = len(error_df)

        # =====================================================
        # 7. NO ERROR FOUND
        # =====================================================

        if error_count == 0:

            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "errors": [],
                "summary": (
                    f"No explicit error logs found "
                    f"for service '{service}'."
                ),
                "confidence": 1.0,
            }

        # =====================================================
        # 8. PREPARE SAMPLE FOR GEMINI
        # =====================================================

        sample_columns = [
            column
            for column in [
                "timestamp",
                "cmdb_id",
                "log_name",
                content_column,
            ]
            if column in error_df.columns
        ]

        sample_df = (
            error_df[
                sample_columns
            ]
            .head(20)
        )

        raw_error_logs = (
            sample_df
            .to_dict(
                orient="records"
            )
        )

        # =====================================================
        # 9. PREPARE GEMINI PROMPT
        # =====================================================

        prompt = f"""
You are an SRE Log Analysis Expert.

Analyze log evidence stored in PostgreSQL.

Investigation ID:
{investigation_id}

Service:
{service}

Incident Time:
{incident_time}

Number of error-related log entries:
{error_count}

The following log samples were retrieved directly
from the investigation_logs table:

{json.dumps(
    raw_error_logs,
    indent=2,
    default=str
)}

Identify meaningful log-based evidence related
to the incident.

IMPORTANT RULES:

- Use ONLY the supplied log evidence.
- Do NOT invent error messages.
- Do NOT invent timestamps.
- Do NOT invent services.
- Distinguish repeated errors from unique errors.
- If the logs do not provide meaningful evidence,
  return an empty errors list.
- The service must be "{service}".
- Return ONLY valid JSON.

Required JSON structure:

{{
    "agent": "Log Agent",
    "evidence_type": "log",
    "errors": [
        {{
            "service": "{service}",
            "timestamp": "{incident_time}",
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
                    response_mime_type="application/json",
                ),
            )

            result = json.loads(
                response.text
            )

            return result

        # =====================================================
        # 11. FALLBACK
        # =====================================================

        except Exception:

            fallback_errors = [
                {
                    "service": service,
                    "timestamp": incident_time,
                    "level": "ERROR",
                    "error_type": "LogAnalysisError",
                    "message": (
                        f"Detected {error_count} "
                        f"error-related log entries "
                        f"for service '{service}'."
                    ),
                    "count": error_count,
                }
            ]

            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "errors": fallback_errors,
                "summary": (
                    f"Detected {error_count} "
                    f"error-related log entries "
                    f"for service '{service}'."
                ),
                "confidence": 0.5,
            }