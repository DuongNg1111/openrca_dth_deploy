from __future__ import annotations
import json
from google import genai
from google.genai import types
from src.process_module.agents.base_agent import BaseAgent
from src.config import load_config  # Import hàm load_config trung tâm

class ReasoningAgent(BaseAgent):
    def __init__(self):
        super().__init__("Reasoning Agent")

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

    def analyze(self, context, metric_result: dict, log_result: dict, trace_result: dict) -> dict:
        # Lấy đúng các mảng dữ liệu đã chuẩn hóa từ 3 agent thành phần
        metric_anomalies = metric_result.get('anomalies', [])
        log_errors = log_result.get('errors', [])
        trace_spans = trace_result.get('traces', [])

        prompt = f"""
        You are an expert Site Reliability Engineer (SRE) AI. Synthesize the findings from the specialized multi-agent telemetry below for service '{context.service}' to determine the definitive root cause (RCA) of the incident.

        [METRIC AGENT EVIDENCE]:
        Summary: {metric_result.get('summary')}
        Anomalies: {json.dumps(metric_anomalies, default=str)}

        [LOG AGENT EVIDENCE]:
        Summary: {log_result.get('summary')}
        Errors: {json.dumps(log_errors, default=str)}

        [TRACE AGENT EVIDENCE]:
        Summary: {trace_result.get('summary')}
        Traces: {json.dumps(trace_spans, default=str)}

        You MUST respond ONLY with a valid JSON object matching this exact structure:
        {{
            "component": "{context.service}",
            "reason": "<Concise Root Cause Title>",
            "confidence": 0.9,
            "occurrence_time": "{context.incident_time}",
            "metrics": {json.dumps(metric_anomalies, default=str)},
            "logs": {json.dumps(log_errors, default=str)},
            "traces": {json.dumps(trace_spans, default=str)},
            "metric_summary": "{metric_result.get('summary', '')}",
            "log_summary": "{log_result.get('summary', '')}",
            "trace_summary": "{trace_result.get('summary', '')}",
            "reasoning": "<Thorough, professional technical root cause analysis>"
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
            result_dict = json.loads(response.text)
            # Đảm bảo luôn gán đúng occurrence_time từ context
            result_dict["occurrence_time"] = context.incident_time
            return result_dict

        except Exception as e:
            return {
                "component": context.service,
                "reason": "Analysis Error",
                "confidence": 0.0,
                "occurrence_time": context.incident_time,
                "metrics": metric_anomalies,
                "logs": log_errors,
                "traces": trace_spans,
                "metric_summary": metric_result.get('summary', ''),
                "log_summary": log_result.get('summary', ''),
                "trace_summary": trace_result.get('summary', ''),
                "reasoning": f"Failed to generate AI conclusion due to error: {str(e)}"
            }