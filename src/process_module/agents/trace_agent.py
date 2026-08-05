from __future__ import annotations
import json
from google import genai
from google.genai import types
from src.process_module.agents.base_agent import BaseAgent
from src.config import load_config  # Import hàm load_config trung tâm

class TraceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Trace Agent")

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
        traces = context.traces
        raw_trace_evidence = []
        max_duration = 0

        # 1. Trích xuất dữ liệu trace thô từ DataFrame giống logic cũ của bạn
        for name, df in (traces.items() if traces else []):
            if df is None or df.empty:
                continue

            if "duration" in df.columns:
                valid_durations = df["duration"].dropna()
                if not valid_durations.empty:
                    max_duration = max(max_duration, valid_durations.max())

                # Lọc các trace có duration cao bất thường (quantile 0.95 hoặc toàn bộ nếu ít)
                high_latency_spans = df[df["duration"] > valid_durations.quantile(0.95)] if len(df) > 1 and not valid_durations.empty else df

                for _, row in high_latency_spans.head(5).iterrows():
                    raw_trace_evidence.append({
                        "trace_file": name,
                        "span_info": {k: str(v) for k, v in row.to_dict().items()}
                    })

        summary_text = f"Max trace duration observed: {max_duration} ms." if max_duration > 0 else "Trace analysis completed, no significant latency spikes."

        # 2. Nếu không tìm thấy trace data, trả về cấu trúc chuẩn rỗng
        if not raw_trace_evidence:
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": [],
                "summary": "Trace analysis completed, no data available.",
                "confidence": 1.0
            }

        # 3. Sử dụng GenAI để phân tích và chuẩn hóa thành danh sách traces chuẩn schema
        prompt = f"""
        You are an SRE Distributed Tracing and Latency Expert. Analyze the following high-latency trace spans extracted for service '{context.service}' during the incident window.
        Raw Trace Evidence: {json.dumps(raw_trace_evidence[:5], default=str)}
        Max Duration Observed: {max_duration} ms

        You MUST respond ONLY with a valid JSON object matching this exact structure:
        {{
            "agent": "Trace Agent",
            "evidence_type": "trace",
            "traces": [
                {{
                    "trace_id": "<extracted trace_id or fallback string>",
                    "root_service": "<root or frontend service name>",
                    "slow_service": "{context.service}",
                    "latency_ms": {float(max_duration)},
                    "normal_latency_ms": 100.0,
                    "dependency": "<downstream dependency like database or redis>",
                    "description": "<detailed professional explanation of the request flow bottleneck>"
                }}
            ],
            "summary": "{summary_text}",
            "confidence": 0.85
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,  # Sử dụng tên model linh hoạt từ config.py
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)

        except Exception as e:
            # Fallback gọn gàng
            fallback_traces = [
                {
                    "trace_id": "unknown_trace",
                    "root_service": "frontend",
                    "slow_service": context.service,
                    "latency_ms": float(max_duration),
                    "normal_latency_ms": float(max_duration) * 0.1 if max_duration > 0 else 100.0,
                    "dependency": "unknown-dependency",
                    "description": f"High latency span detected with duration {max_duration} ms. (API Rate Limit / Fallback)"
                }
            ]
            return {
                "agent": "Trace Agent",
                "evidence_type": "trace",
                "traces": fallback_traces,
                "summary": summary_text,
                "confidence": 0.6
            }