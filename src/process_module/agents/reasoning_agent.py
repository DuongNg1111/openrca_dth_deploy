from __future__ import annotations
import json
from google import genai
from google.genai import types
from src.process_module.agents.base_agent import BaseAgent

class ReasoningAgent(BaseAgent):
    def __init__(self):
        super().__init__("Reasoning Agent")
        self.client = genai.Client()

    def analyze(self, context, metric_result: dict, log_result: dict, trace_result: dict) -> dict:
        prompt = f"""
        You are an expert Site Reliability Engineer (SRE) AI. Analyze the multi-agent telemetry summaries below for service '{context.service}' to identify the root cause of the incident.

        [METRIC AGENT SUMMARY]:
        {metric_result.get('summary')}
        Evidence: {json.dumps(metric_result.get('evidence', []))}

        [LOG AGENT SUMMARY]:
        {log_result.get('summary')}
        Evidence: {json.dumps(log_result.get('evidence', []))}

        [TRACE AGENT SUMMARY]:
        {trace_result.get('summary')}
        Evidence: {json.dumps(trace_result.get('evidence', []))}

        You MUST respond ONLY with a valid JSON object matching this exact structure, with no markdown formatting around it if possible:
        {{
            "component": "{context.service}",
            "reason": "<Short root cause title, e.g., Database timeout or CPU saturation>",
            "confidence": <float between 0.0 and 1.0>,
            "metrics": {json.dumps(metric_result.get('evidence', []))},
            "logs": {json.dumps(log_result.get('evidence', []))},
            "traces": {json.dumps(trace_result.get('evidence', []))},
            "metric_summary": "{metric_result.get('summary', '')}",
            "log_summary": "{log_result.get('summary', '')}",
            "trace_summary": "{trace_result.get('summary', '')}",
            "reasoning": "<Detailed technical explanation of why this is the root cause based on the multi-agent evidence>"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                ),
            )
            result_dict = json.loads(response.text)
            # Gắn occurrence_time dạng datetime chuẩn từ context
            result_dict["occurrence_time"] = context.incident_time
            return result_dict

        except Exception as e:
            return {
                "component": context.service,
                "reason": "Analysis Error",
                "confidence": 0.0,
                "occurrence_time": context.incident_time,
                "metrics": metric_result.get('evidence', []),
                "logs": log_result.get('evidence', []),
                "traces": trace_result.get('evidence', []),
                "metric_summary": metric_result.get('summary', ''),
                "log_summary": log_result.get('summary', ''),
                "trace_summary": trace_result.get('summary', ''),
                "reasoning": f"Failed to generate AI conclusion: {str(e)}"
            }