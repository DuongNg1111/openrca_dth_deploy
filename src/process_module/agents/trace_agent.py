from __future__ import annotations

import json
import pandas as pd

from google import genai
from google.genai import types

from src.process_module.agents.base_agent import BaseAgent
from src.database.repository import get_investigation_traces


class TraceAgent(BaseAgent):

    def __init__(self):
        super().__init__("Trace Agent")

    def analyze(self, context) -> dict:
        """
        Analyze traces stored in PostgreSQL.

        Flow:
            investigation_traces
                    ↓
            query by investigation_id
                    ↓
            filter by service
                    ↓
            calculate latency statistics
                    ↓
            detect high-latency traces
                    ↓
            Gemini analysis
                    ↓
            return structured trace evidence
                    ↓
            full_pipeline saves evidence to evidence_records
        """

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
        # 1. VALIDATE INVESTIGATION ID
        # =====================================================

        if investigation_id is None:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    "Trace analysis skipped because "
                    "investigation_id was not provided."
                ),
                "confidence": 0.0
            }

        # =====================================================
        # 2. LOAD TRACES FROM DATABASE
        # =====================================================

        try:
            traces_df = get_investigation_traces(
                investigation_id
            )

        except Exception as e:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    f"Failed to load traces for "
                    f"investigation {investigation_id}: "
                    f"{str(e)}"
                ),
                "confidence": 0.0
            }

        # =====================================================
        # 3. CHECK DATA
        # =====================================================

        if traces_df is None or traces_df.empty:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    f"No trace data found for "
                    f"investigation {investigation_id}."
                ),
                "confidence": 1.0
            }

        # =====================================================
        # 4. VALIDATE COLUMNS
        # =====================================================

        required_columns = [
            "timestamp",
            "cmdb_id",
            "span_id",
            "trace_id",
            "duration",
            "type",
            "status_code",
            "operation_name",
            "parent_span"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in traces_df.columns
        ]

        if missing_columns:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    "Trace table is missing required columns: "
                    + ", ".join(missing_columns)
                ),
                "confidence": 0.0
            }
        # =====================================================
        # 5. FILTER BY SERVICE
        # =====================================================

        if "cmdb_id" not in traces_df.columns:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    "Trace table is missing required column: cmdb_id"
                ),
                "confidence": 0.0
            }

        service_df = traces_df[
            traces_df["cmdb_id"].astype(str).str.lower()
            == str(service).lower()
        ].copy()

        if service_df.empty:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    f"No trace data found for service '{service}'."
                ),
                "confidence": 1.0
            }

        # =====================================================
        # 6. CLEAN DURATION
        # =====================================================

        service_df["duration"] = pd.to_numeric(
            service_df["duration"],
            errors="coerce"
        )

        service_df = service_df.dropna(
            subset=["duration"]
        )

        service_df["duration_ms"] = (
            service_df["duration"] / 1000.0
        )

        if service_df.empty:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    f"No valid trace duration values "
                    f"were found for service '{service}'."
                ),
                "confidence": 1.0
            }

        # duration trong PostgreSQL là microseconds
        # Convert sang milliseconds cho Agent output
        service_df["duration_ms"] = (
            service_df["duration"] / 1000.0
        )
        # =====================================================
        # 7. CALCULATE LATENCY STATISTICS
        # =====================================================

        max_duration = float(
            service_df["duration_ms"].max()
        )

        mean_duration = float(
            service_df["duration_ms"].mean()
        )

        median_duration = float(
            service_df["duration_ms"].median()
        )

        p95_duration = float(
            service_df["duration_ms"].quantile(0.95)
        )

        p99_duration = float(
            service_df["duration_ms"].quantile(0.99)
        )

        sample_count = int(
            len(service_df)
        )
        # =====================================================
        # 8. IDENTIFY HIGH-LATENCY TRACES
        # =====================================================

        high_latency_df = service_df[
            service_df["duration_ms"] >= p95_duration
        ].copy()

        high_latency_df = high_latency_df.sort_values(
            by="duration_ms",
            ascending=False
        )

        sample_df = high_latency_df.head(20)

        # =====================================================
        # 9. BUILD RAW TRACE EVIDENCE
        # =====================================================

        sample_columns = [
            column
            for column in [
                "timestamp",
                "cmdb_id",
                "span_id",
                "trace_id",
                "duration_ms",
                "type",
                "status_code",
                "operation_name",
                "parent_span"
            ]
            if column in sample_df.columns
        ]

        raw_trace_evidence = (
            sample_df[
                sample_columns
            ]
            .to_dict(
                orient="records"
            )
        )
        # =====================================================
        # 10. PREPARE SUMMARY
        # =====================================================

        summary_text = (
            f"Service '{service}' has "
            f"{sample_count} trace records. "
            f"Mean latency: {mean_duration:.2f} ms, "
            f"median: {median_duration:.2f} ms, "
            f"P95: {p95_duration:.2f} ms, "
            f"P99: {p99_duration:.2f} ms, "
            f"maximum: {max_duration:.2f} ms."
        )
        # =====================================================
        # 11. GEMINI PROMPT
        # =====================================================

        prompt = f"""
You are an SRE Distributed Tracing and Latency Analysis Expert.

Analyze trace evidence stored in PostgreSQL.

Investigation ID:
{investigation_id}

Service:
{service}

Incident Time:
{incident_time}

Trace Statistics:

Total trace records:
{sample_count}

Mean latency:
{mean_duration}

Median latency:
{median_duration}

P95 latency:
{p95_duration}

P99 latency:
{p99_duration}

Maximum latency:
{max_duration}

Representative high-latency trace records:

{json.dumps(
    raw_trace_evidence,
    indent=2,
    default=str
)}

IMPORTANT RULES:

1. Use ONLY the supplied trace data.
2. Do NOT invent trace IDs.
3. Do NOT invent services.
4. Do NOT invent dependencies.
5. Do NOT invent latency values.
6. The slow_service MUST be "{service}".
7. Do NOT infer a dependency from operation_name alone.
8. If parent_span is empty, null, or NaN, return dependency as "".
9. Do NOT infer root_service unless explicitly supported by the data.
10. operation_name may describe the operation, but do not assume it is a dependency.
11. If root service or dependency cannot be determined from the supplied data,
    return an empty string.
12. If there is insufficient evidence of a meaningful latency anomaly,
    return an empty traces list.
13. Return ONLY valid JSON.

Required JSON structure:

{{
    "agent": "Trace Agent",
    "evidence_type": "trace",
    "traces": [
        {{
            "trace_id": "",
            "root_service": "",
            "slow_service": "{service}",
            "latency_ms": 0.0,
            "normal_latency_ms": {median_duration},
            "dependency": "",
            "description": ""
        }}
    ],
    "summary": "",
    "confidence": 0.0
}}
"""

        # =====================================================
        # 12. CALL GEMINI
        # =====================================================

        try:

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                ),
            )

            result = json.loads(
                response.text
            )

            return result

        # =====================================================
        # 13. FALLBACK
        # =====================================================

        except Exception as e:

            fallback_traces = []

            for item in raw_trace_evidence[:5]:

                duration_value = item.get(
                    "duration_ms",
                    0.0
                )

                try:
                    duration_value = float(
                        duration_value
                    )
                except (TypeError, ValueError):
                    duration_value = 0.0

                fallback_traces.append(
                    {
                        "trace_id": str(
                            item.get(
                                "trace_id",
                                ""
                            )
                        ),

                        "root_service": "",

                        "slow_service": service,

                        "latency_ms": duration_value,

                        "normal_latency_ms": (
                            median_duration
                        ),

                        "dependency": "",

                        "description": (
                            f"High-latency trace detected "
                            f"for service '{service}' "
                            f"with duration "
                            f"{duration_value}. "
                            f"Gemini analysis unavailable."
                        )
                    }
                )

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": fallback_traces,
                "summary": summary_text,
                "confidence": 0.5
            }