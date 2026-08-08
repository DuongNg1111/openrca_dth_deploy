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
                "summary": str(e),
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
        # 3. CLEAN DATA
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
        # 4. FIND TARGET SERVICE TRACE
        # ============================================

        service_trace_ids = set(
            df[
                df["cmdb_id"]
                .astype(str)
                .str.contains(
                    service.replace("-0",""),
                    case=False,
                    na=False
                )
            ]["trace_id"]
            .tolist()
        )



        if not service_trace_ids:

            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": (
                    f"No traces related to "
                    f"service {service}"
                ),
                "confidence": 1.0
            }



        # lấy toàn bộ span trong trace đó
        related_df = df[
            df["trace_id"].isin(
                service_trace_ids
            )
        ].copy()



        # ============================================
        # 5. STATISTICS
        # ============================================

        median_latency = float(
            related_df["duration_ms"].median()
        )


        p95_latency = float(
            related_df["duration_ms"]
            .quantile(0.95)
        )



        anomaly_df = related_df[
            related_df["duration_ms"]
            >= p95_latency
        ]


        anomaly_df = anomaly_df.sort_values(
            "duration_ms",
            ascending=False
        )


        sample = related_df.sort_values(
            "duration_ms",
            ascending=False
        ).head(50)



        raw_trace = []


        for _, row in sample.iterrows():

            raw_trace.append(

                    {
                        "trace_id":
                            str(row["trace_id"]),

                        "service":
                            str(row["cmdb_id"]),

                        "span_id":
                            str(row["span_id"]),

                        "parent_span":
                            str(row["parent_span"]),

                        "operation":
                            str(row["operation_name"]),

                        "latency_ms":
                            float(row["duration_ms"]),

                        "is_anomaly":
                            bool(
                                row["duration_ms"]
                                >= p95_latency
                            )
                        }
            )


        if not raw_trace:

            return {

                "agent": "Trace Agent",

                "evidence_type": "trace",

                "traces": [],

                "summary":
                    "No latency anomaly detected.",

                "confidence": 1.0
            }



        # ============================================
        # 6. GEMINI ANALYSIS
        # ============================================

        prompt = f"""

    You are an SRE Distributed Tracing Expert.

    Analyze ONLY the supplied trace evidence.

    IMPORTANT CONTEXT:

    The target service provided by the investigation context is a logical service name.

    The trace data may contain runtime service/container names
    that are slightly different from the logical service name.

    Example:
    - Logical service: frontend-0
    - Runtime trace service: frontend2-0

    These should be considered related evidence if they represent the same service family.

    Do NOT discard trace evidence only because the cmdb_id
    does not exactly match the logical service name.


    Target logical service:
    {service}


    Incident time:
    {incident_time}


    Median latency:
    {median_latency} ms


    Trace evidence:

    {json.dumps(
        raw_trace,
        indent=2
    )}


    Rules:

    1. Use ONLY the supplied trace evidence.
    2. Do NOT invent services.
    3. Do NOT rename services.
    4. Keep the original runtime service name from cmdb_id.
    5. The "service" field in output MUST contain the original trace cmdb_id.
    6. The context service name is only used to identify related traces.
    7. Runtime service names with similar prefixes should be treated as related evidence.
    8. Do NOT assume dependency only from operation_name.
    9. A dependency is valid only when parent_span matches another span_id in the supplied trace evidence.
    10. If dependency cannot be proven, return an empty string.
    11. Do NOT invent root services.
    12. Return only meaningful latency anomalies.
    13. If latency is not significantly higher than the baseline, do not include it.
    14. Return ONLY valid JSON.


    Required JSON format:

    {{
    "agent":"Trace Agent",

    "evidence_type":"trace",

    "traces":[

    {{
    "trace_id":"",
    "service":"",
    "operation":"",
    "latency_ms":0,
    "baseline_ms":0,
    "dependency":"",
    "description":""
    }}

    ],

    "summary":"",

    "confidence":0.0

    }}

    """

            # ============================================
        # 7. CALL GEMINI
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

            text = response.text.strip()

            print("\n========== TRACE RESPONSE ==========")
            print(text)
            print("=====================================")

            while text.count("{") > text.count("}"):
                text += "}"

            while text.count("[") > text.count("]"):
                text += "]"

            result = json.loads(text)

            return result

        # ============================================
        # 8. FALLBACK
        # ============================================

        except Exception as e:


            fallback = []


            for item in raw_trace[:10]:


                fallback.append(

                    {
                        "trace_id":
                            item["trace_id"],


                        "service":
                            item["service"],


                        "operation":
                            item["operation"],


                        "latency_ms":
                            item["latency_ms"],


                        "baseline_ms":
                            median_latency,


                        "dependency":
                            "",


                        "description":
                            (
                                f"High latency detected "
                                f"in {item['service']} "
                                f"operation "
                                f"{item['operation']}"
                            )

                    }

                )


            return {


                "agent":
                    "Trace Agent",


                "evidence_type":
                    "trace",


                "traces":
                    fallback,


                "summary":
                    (
                        f"Detected latency anomalies "
                        f"for service {service}"
                    ),


                "confidence":
                    0.5

            }