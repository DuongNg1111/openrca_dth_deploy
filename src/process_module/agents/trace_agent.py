from __future__ import annotations

import json

import pandas as pd
from google import genai
from google.genai import types

from src.config import load_config
from src.database.repository import get_investigation_traces
from src.process_module.agents.base_agent import BaseAgent


class TraceAgent(BaseAgent):

    def __init__(self, config=None):
        super().__init__("Trace Agent", config=config)

        # Load cấu hình từ config.py
        self.config = config if config is not None else load_config()

        llm_cfg = self.config.get("llm", {})

        # Lấy API key và model từ config chung
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

        # ============================================
        # 1. VALIDATE
        # ============================================

        if investigation_id is None:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": "Missing investigation_id.",
                "confidence": 0.0
            }

        # ============================================
        # 2. LOAD TRACE DATA
        # ============================================

        try:

            traces_df = get_investigation_traces(
                investigation_id,
                service=service
            )

        except Exception as e:

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": f"Failed loading traces: {str(e)}",
                "confidence": 0.0
            }

        if traces_df is None or traces_df.empty:

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": "No trace data found.",
                "confidence": 1.0
            }

        # ============================================
        # 3. VALIDATE REQUIRED COLUMNS
        # ============================================

        required_columns = [
            "duration",
            "cmdb_id",
            "trace_id",
            "span_id",
            "parent_span",
            "operation_name"
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

        # ============================================
        # 4. CLEAN DATA
        # ============================================

        df = traces_df.copy()

        df["duration"] = pd.to_numeric(
            df["duration"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["duration"]
        )

        if df.empty:

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": "No valid duration.",
                "confidence": 1.0
            }

        # PostgreSQL duration = microseconds
        df["duration_ms"] = (
            df["duration"] / 1000
        )

        # ============================================
        # 5. FIND TARGET SERVICE TRACE
        # ============================================

        runtime_service = (
            str(service)
            .replace("-0", "")
            .strip()
            .lower()
        )

        cmdb_series = (
            df["cmdb_id"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        # Exact logical service match
        service_trace_ids = set(
            df[
                cmdb_series == runtime_service
            ]["trace_id"].tolist()
        )

        # Support service instances:
        # productcatalogservice-0
        # productcatalogservice-1
        # productcatalogservice-2
        if not service_trace_ids:

            service_trace_ids = set(
                df[
                    cmdb_series.str.fullmatch(
                        rf"{runtime_service}-\d+"
                    )
                ]["trace_id"].tolist()
            )

        if not service_trace_ids:

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    f"No traces related to service {service}"
                ),
                "confidence": 1.0
            }

        # Get all spans belonging to those traces
        related_df = df[
            df["trace_id"].isin(service_trace_ids)
        ].copy()

        if related_df.empty:

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    f"No related trace spans found "
                    f"for service {service}"
                ),
                "confidence": 1.0
            }

        # ============================================
        # 6. STATISTICS
        # ============================================

        median_latency = float(
            related_df["duration_ms"].median()
        )

        p95_latency = float(
            related_df["duration_ms"].quantile(0.95)
        )

        anomaly_df = related_df[
            related_df["duration_ms"] >= p95_latency
        ].sort_values(
            "duration_ms",
            ascending=False
        )

        # Keep top 50 spans as evidence
        sample = (
            related_df
            .sort_values(
                "duration_ms",
                ascending=False
            )
            .head(50)
        )

        # ============================================
        # 7. BUILD TRACE EVIDENCE
        # ============================================

        raw_trace = []

        for _, row in sample.iterrows():

            timestamp = ""

            if (
                "timestamp" in row.index
                and row["timestamp"] is not None
            ):
                timestamp = str(row["timestamp"])

            raw_trace.append(
                {
                    "trace_id": str(
                        row["trace_id"]
                    ),

                    "service": str(
                        row["cmdb_id"]
                    ),

                    "span_id": str(
                        row["span_id"]
                    ),

                    "parent_span": str(
                        row["parent_span"]
                    ),

                    "operation": str(
                        row["operation_name"]
                    ),

                    "timestamp": timestamp,

                    "latency_ms": float(
                        row["duration_ms"]
                    ),

                    "is_anomaly": bool(
                        row["duration_ms"] >= p95_latency
                    )
                }
            )

        if not raw_trace:

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": "No latency anomaly detected.",
                "confidence": 1.0
            }

        # ============================================
        # 8. GEMINI PROMPT
        # ============================================

        prompt = f"""
You are an SRE Distributed Tracing Expert.

Analyze ONLY the supplied trace evidence.

IMPORTANT CONTEXT:

The target service provided by the investigation context
is a logical service name.

The trace data may contain runtime service/container names
that are slightly different from the logical service name.

Example:
- Logical service: frontend-0
- Runtime trace service: frontend2-0

These should be considered related evidence if they
represent the same service family.

Do NOT discard trace evidence only because the cmdb_id
does not exactly match the logical service name.

Target logical service:
{service}

Incident time:
{incident_time}

Median latency:
{median_latency} ms

P95 latency:
{p95_latency} ms

Trace evidence:

{json.dumps(
    raw_trace,
    indent=2,
    default=str
)}

Rules:

1. Use ONLY the supplied trace evidence.
2. Do NOT invent services.
3. Do NOT rename services.
4. Keep the original runtime service name from cmdb_id.
5. The "service" field in output MUST contain the original trace cmdb_id.
6. The context service name is only used to identify related traces.
7. Runtime service names with similar prefixes may be treated as related evidence.
8. Do NOT assume dependency only from operation_name.
9. A dependency is valid only when parent_span matches another span_id in the supplied trace evidence.
10. If dependency cannot be proven, return an empty string.
11. Do NOT invent root services.
12. Return only meaningful latency anomalies.
13. If latency is not significantly higher than the baseline, do not include it.
14. Use the supplied latency and baseline values only.
15. Return ONLY valid JSON.

Required JSON format:

{{
    "agent": "Trace Agent",
    "evidence_type": "trace",
    "traces": [
        {{
            "trace_id": "",
            "service": "",
            "operation": "",
            "timestamp": "",
            "latency_ms": 0,
            "baseline_ms": 0,
            "dependency": "",
            "description": ""
        }}
    ],
    "summary": "",
    "confidence": 0.0
}}
"""

        # ============================================
        # 9. CALL GEMINI
        # ============================================

        try:

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )

            response_text = getattr(
                response,
                "text",
                None
            )

            if not response_text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            text = response_text.strip()

            print("\n========== TRACE RESPONSE ==========")
            print(text)
            print("=====================================")

            result = json.loads(text)

            if not isinstance(result, dict):
                raise ValueError(
                    "Trace Agent response must be a JSON object."
                )

            result.setdefault(
                "agent",
                "Trace Agent"
            )

            result.setdefault(
                "evidence_type",
                "trace"
            )

            result.setdefault(
                "traces",
                []
            )

            result.setdefault(
                "summary",
                ""
            )

            result.setdefault(
                "confidence",
                0.0
            )

            return result

        # ============================================
        # 10. FALLBACK
        # ============================================

        except Exception as e:

            fallback = []

            # Use top latency spans as fallback evidence
            for item in raw_trace[:10]:

                fallback.append(
                    {
                        "trace_id": item["trace_id"],

                        "service": item["service"],

                        "operation": item["operation"],

                        "timestamp": item.get(
                            "timestamp",
                            ""
                        ),

                        "latency_ms": item[
                            "latency_ms"
                        ],

                        "baseline_ms": median_latency,

                        "dependency": "",

                        "description": (
                            f"High latency detected "
                            f"in {item['service']} "
                            f"operation "
                            f"{item['operation']}."
                        )
                    }
                )

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": fallback,
                "summary": (
                    f"Detected latency anomalies "
                    f"for service {service}. "
                    "Gemini analysis unavailable; "
                    "fallback trace evidence was returned."
                ),
                "confidence": 0.5
            }