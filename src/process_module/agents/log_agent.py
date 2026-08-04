from __future__ import annotations
import json
from google import genai
from google.genai import types
from src.process_module.agents.base_agent import BaseAgent
from src.config import load_config

class LogAgent(BaseAgent):
    def __init__(self):
        super().__init__("Log Agent")

        # Load cấu hình từ config.py (đã bao gồm đọc .env và file yaml)
        self.config = load_config()
        llm_cfg = self.config.get("llm", {})

        # Lấy api_key và model từ config trung tâm
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get("model", "gemini-3.5-flash")

        # Khởi tạo client Gemini
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def analyze(self, context) -> dict:
        logs = context.logs
        raw_error_logs = []
        error_count = 0

        # 1. Trích xuất các dòng log lỗi từ DataFrame
        for name, df in (logs.items() if logs else []):
            if df is None or df.empty:
                continue

            text_columns = [col for col in df.columns if df[col].dtype == object]
            for col in text_columns:
                error_rows = df[df[col].astype(str).str.contains("error|exception|timeout|fail|slow", case=False, na=False)]
                if not error_rows.empty:
                    error_count += len(error_rows)
                    for _, row in error_rows.head(10).iterrows():  # Lấy mẫu tối đa 10 dòng tiêu biểu
                        raw_error_logs.append({
                            "log_file": name,
                            "content": row.to_dict()
                        })

        # 2. Nếu không tìm thấy log lỗi, trả về cấu trúc chuẩn với danh sách errors trống
        if error_count == 0 or not raw_error_logs:
            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "errors": [],
                "summary": "No explicit error logs found in the given time window.",
                "confidence": 1.0
            }

        # 3. Sử dụng GenAI để phân tích và chuẩn hóa các log thô thành cấu trúc mong muốn
        prompt = f"""
        You are an SRE Log Analysis Expert. Analyze the following raw error logs extracted from service '{context.service}' during the incident window.
        Raw Error Logs Sample: {json.dumps(raw_error_logs[:10], default=str)}
        Total error entries found: {error_count}

        You MUST respond ONLY with a valid JSON object matching this exact structure:
        {{
            "agent": "Log Agent",
            "evidence_type": "log",
            "errors": [
                {{
                    "service": "{context.service}",
                    "timestamp": "{context.incident_time}",
                    "level": "ERROR",
                    "error_type": "<Extracted error type name, e.g., DatabaseConnectionTimeout>",
                    "message": "<Summarized error message description>",
                    "count": {error_count}
                }}
            ],
            "summary": "<Short professional summary of log errors>",
            "confidence": 0.9
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,  # Lấy linh hoạt tên model từ config.py
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)

        except Exception as e:
            # Fallback nếu gọi AI lỗi nhưng vẫn giữ nguyên form chuẩn cấu trúc nhóm đề ra
            return {
                "agent": "Log Agent",
                "evidence_type": "log",
                "errors": [
                    {
                        "service": context.service,
                        "timestamp": context.incident_time,
                        "level": "ERROR",
                        "error_type": "LogAnalysisError",
                        "message": f"Detected {error_count} raw error entries, but AI formatting failed: {str(e)}",
                        "count": error_count
                    }
                ],
                "summary": f"Detected {error_count} error/timeout log entries.",
                "confidence": 0.5
            }