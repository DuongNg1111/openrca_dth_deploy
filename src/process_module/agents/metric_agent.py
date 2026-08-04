from __future__ import annotations
import json
from google import genai
from google.genai import types
from src.process_module.agents.base_agent import BaseAgent
from src.config import load_config  # Import hàm load_config trung tâm

class MetricAgent(BaseAgent):
    def __init__(self):
        super().__init__("Metric Agent")

        # Load cấu hình từ config.py (đã bao gồm đọc .env và file yaml)
        self.config = load_config()
        llm_cfg = self.config.get("llm", {})

        # Lấy api_key và model từ cấu hình chung
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get("model", "gemini-3.5-flash")

        # Khởi tạo client Gemini với api_key (nếu có)
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def analyze(self, context) -> dict:
        metrics = context.metrics
        raw_metric_evidence = []
        summaries = []

        # 1. Trích xuất dữ liệu metric thô từ DataFrame giống logic cũ của bạn
        for name, df in (metrics.items() if metrics else []):
            if df is None or df.empty or "value" not in df.columns:
                continue

            if "kpi_name" in df.columns:
                for kpi in df["kpi_name"].unique():
                    kpi_df = df[df["kpi_name"] == kpi]
                    if not kpi_df.empty:
                        kpi_max = float(kpi_df["value"].max())
                        kpi_mean = float(kpi_df["value"].mean())
                        raw_metric_evidence.append({
                            "metric_file": name,
                            "metric": kpi,
                            "max_value": kpi_max,
                            "mean_value": kpi_mean
                        })
                        summaries.append(f"KPI '{kpi}' reached max value {kpi_max:.2f}")
            else:
                max_val = float(df["value"].max())
                mean_val = float(df["value"].mean())
                raw_metric_evidence.append({
                    "metric_file": name,
                    "metric": "general_value",
                    "max_value": max_val,
                    "mean_value": mean_val
                })
                summaries.append(f"Metric max value {max_val:.2f}")

        # 2. Nếu không có metric data, trả về cấu trúc chuẩn rỗng
        if not raw_metric_evidence:
            return {
                "agent": "Metric Agent",
                "evidence_type": "metric",
                "anomalies": [],
                "summary": "No metric anomalies detected within the window.",
                "confidence": 1.0
            }

        summary_text = ", ".join(summaries) if summaries else "Metrics analyzed."

        # 3. Sử dụng GenAI để chuẩn hóa thành các anomalies có mức độ ảnh hưởng (severity, baseline, description)
        prompt = f"""
        You are an SRE Metric and Performance Analysis Expert. Analyze the following metric statistics extracted for service '{context.service}' during the incident window.
        Extracted Metric Statistics: {json.dumps(raw_metric_evidence)}

        You MUST respond ONLY with a valid JSON object matching this exact structure:
        {{
            "agent": "Metric Agent",
            "evidence_type": "metric",
            "anomalies": [
                {{
                    "metric": "<metric or kpi name, e.g., mrt or cpu_usage>",
                    "service": "{context.service}",
                    "value": 0.0,
                    "baseline": 0.0,
                    "timestamp": "{context.incident_time}",
                    "severity": "<critical | warning | normal>",
                    "description": "<detailed professional explanation of the metric anomaly compared to baseline>"
                }}
            ],
            "summary": "{summary_text}",
            "confidence": 0.8
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,  # Sử dụng tên model được cấu hình linh hoạt từ config.py
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)

        except Exception as e:
            # Fallback nếu gọi AI lỗi nhưng vẫn giữ nguyên form chuẩn cấu trúc nhóm đề ra
            fallback_anomalies = [
                {
                    "metric": item.get("metric", "unknown"),
                    "service": context.service,
                    "value": item.get("max_value", 0.0),
                    "baseline": item.get("mean_value", 0.0),
                    "timestamp": context.incident_time,
                    "severity": "warning",
                    "description": f"Observed peak value {item.get('max_value', 0.0)} with mean {item.get('mean_value', 0.0)}. AI formatting failed: {str(e)}"
                }
                for item in raw_metric_evidence
            ]
            return {
                "agent": "Metric Agent",
                "evidence_type": "metric",
                "anomalies": fallback_anomalies,
                "summary": summary_text,
                "confidence": 0.6
            }