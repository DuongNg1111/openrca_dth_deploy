from __future__ import annotations

import json

from google.genai import types

from src.database.repository import get_investigation_metrics
from src.process_module.agents.base_agent import BaseAgent


class MetricAgent(BaseAgent):

        # Load cấu hình từ config.py (đã bao gồm đọc .env và file yaml)
        self.config = load_config()
        llm_cfg = self.config.get("llm", {})

        # Lấy api_key và model từ cấu hình chung
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get("model")

        # Khởi tạo client Gemini với api_key (nếu có)
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def analyze(self, context) -> dict:
        """
        Analyze metrics stored in PostgreSQL for the current investigation.

        IMPORTANT:
        This agent no longer reads context.metrics.
        All metric data must come from investigation_metrics.
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
                "agent": "Metric Agent",
                "evidence_type": "metric",
                "anomalies": [],
                "summary": (
                    "Metric analysis skipped because "
                    "investigation_id was not provided."
                ),
                "confidence": 0.0
            }

        # =====================================================
        # 2. LOAD METRICS FROM DATABASE
        # =====================================================

        try:
            df = get_investigation_metrics(
                investigation_id,
                service=service
            )

        except Exception as e:
            return {
                "agent": "Metric Agent",
                "evidence_type": "metric",
                "anomalies": [],
                "summary": (
                    f"Failed to load metrics for "
                    f"investigation {investigation_id}: {str(e)}"
                ),
                "confidence": 0.0
            }

        # =====================================================
        # 3. CHECK DATA
        # =====================================================

        if df is None or df.empty:
            return {
                "agent": "Metric Agent",
                "evidence_type": "metric",
                "anomalies": [],
                "summary": (
                    f"No metric data found for "
                    f"investigation {investigation_id}."
                ),
                "confidence": 1.0
            }

        # =====================================================
        # 4. VALIDATE REQUIRED COLUMNS
        # =====================================================

        required_columns = [
            "timestamp",
            "cmdb_id",
            "kpi_name",
            "value"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            return {
                "agent": "Metric Agent",
                "evidence_type": "metric",
                "anomalies": [],
                "summary": (
                    "Metric table is missing required columns: "
                    + ", ".join(missing_columns)
                ),
                "confidence": 0.0
            }

        # =====================================================
        # 5. CLEAN NUMERIC VALUES
        # =====================================================

        df = df.copy()

        df["value"] = (
            df["value"]
            .astype(str)
            .str.strip()
        )

        df["value"] = (
            df["value"]
            .replace(
                ["", "nan", "None", "null"],
                None
            )
        )

        df["value"] = (
            __import__("pandas")
            .to_numeric(
                df["value"],
                errors="coerce"
            )
        )

        df = df.dropna(
            subset=["value"]
        )

        if df.empty:
            return {
                "agent": "Metric Agent",
                "evidence_type": "metric",
                "anomalies": [],
                "summary": (
                    "No valid numeric metric values "
                    "were found."
                ),
                "confidence": 1.0
            }

        # =====================================================
        # 6. BUILD METRIC EVIDENCE
        # =====================================================

        raw_metric_evidence = []

        summaries = []


        grouped = df.groupby(
            ["cmdb_id", "kpi_name"],
            dropna=False
        )


        for (cmdb_id, kpi_name), kpi_df in grouped:

            if kpi_df.empty:
                continue


            # baseline
            mean_value = float(
                kpi_df["value"].mean()
            )


            # peak point
            max_row = (
                kpi_df
                .sort_values(
                    "value",
                    ascending=False
                )
                .iloc[0]
            )


            max_value = float(
                max_row["value"]
            )


            deviation_ratio = (
                max_value / mean_value
                if mean_value != 0
                else 0
            )


            raw_metric_evidence.append(

                {
                    "cmdb_id":
                        str(cmdb_id),

                    "metric":
                        str(kpi_name),

                    "peak_value":
                        max_value,

                    "baseline_mean":
                        mean_value,

                    "deviation_ratio":
                        round(
                            deviation_ratio,
                            2
                        ),

                    "peak_timestamp":
                        str(
                            max_row["timestamp"]
                        ),

                    "sample_count":
                        int(
                            len(kpi_df)
                        )
                }

            )


            summaries.append(

                f"{kpi_name} "
                f"(CMDB: {cmdb_id}) "
                f"peak={max_value:.2f}, "
                f"baseline={mean_value:.2f}"

            )



        # =====================================================
        # 7. NO STATISTICS
        # =====================================================

        if not raw_metric_evidence:

            return {

                "agent":
                    "Metric Agent",

                "evidence_type":
                    "metric",

                "anomalies":
                    [],

                "summary":
                    "No usable metric statistics were found.",

                "confidence":
                    1.0

            }



        summary_text = (

            " | ".join(
                summaries
            )

            if summaries

            else "Metrics analyzed."

        )

        # =====================================================
        # 8. PREPARE GEMINI PROMPT
        # =====================================================


        prompt = f"""

    You are an SRE Metric Performance Analysis Expert.

    Analyze ONLY the supplied metric statistics.

    Investigation ID:
    {investigation_id}


    Target service:
    {service}


    Incident time:
    {incident_time}


    Metric statistics generated directly from PostgreSQL
    investigation_metrics table:


    {json.dumps(
        raw_metric_evidence,
        indent=2,
        default=str
    )}



    Your task:

    Identify meaningful metric anomalies related to the incident.



    STRICT RULES:

    1. Use ONLY supplied metric statistics.

    2. Do NOT invent metric names.

    3. Do NOT invent metric values.

    4. Do NOT invent timestamps.

    5. Do NOT rename services.

    6. Always use service name:
    "{service}"


    7. Output mapping:

    - value = max_value
    - baseline = mean_value
    - timestamp = max_timestamp


    8. Prioritize abnormal performance indicators:

    - request duration
    - latency
    - response time
    - timeout related metrics
    - error related metrics


    9. A metric should be considered suspicious when:

    - max_value is significantly higher than mean_value
    - latency/request duration reaches unusually high values
    - the metric represents possible service degradation


    10. Normal infrastructure metrics
    (CPU, memory, filesystem, network)
    should NOT be reported unless they show clear abnormal deviation.


    11. If no meaningful anomaly exists,
    return an empty anomalies list.


    12. Return ONLY valid JSON.



    Required JSON format:


    {{
    "agent": "Metric Agent",

    "evidence_type": "metric",

    "anomalies":
    [

    {{
    "metric": "",

    "service": "{service}",

    "value": 0.0,

    "baseline": 0.0,

    "timestamp": "",

    "severity": "",

    "description": ""
    }}

    ],


    "summary": "",

    "confidence": 0.0

    }}

    """

        # =====================================================
        # 9. CALL GEMINI
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

        except Exception as e:
            # Fallback gọn gàng, không nhét chuỗi JSON lỗi dài dòng của Google API vào description
            fallback_anomalies = [
                {
                    "metric": item.get(
                        "metric",
                        "unknown"
                    ),

                    "service": service,

                    "value": item.get(
                        "peak_value",
                        0.0
                    ),

                    "baseline": item.get(
                        "baseline_mean",
                        0.0
                    ),

                    "timestamp": item.get(
                        "peak_timestamp",
                        ""
                    ),

                    "severity": "warning",
                    "description": f"Observed peak value {item.get('max_value', 0.0)} with mean {item.get('mean_value', 0.0)}. (API Rate Limit / Fallback)"
                }
            )

        return {
            "agent": "Metric Agent",
            "evidence_type": "metric",
            "anomalies": fallback_anomalies,
            "summary": summary_text,
            "confidence": 0.6
        }
