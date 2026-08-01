from __future__ import annotations
from src.process_module.agents.base_agent import BaseAgent

class LogAgent(BaseAgent):
    def __init__(self):
        super().__init__("Log Agent")

    def analyze(self, context):
        logs = context.logs
        evidence = []
        error_count = 0

        for name, df in logs.empty and {} or logs.items():
            if df.empty:
                continue

            # Tìm kiếm các dòng log chứa thông tin lỗi hoặc exception
            text_columns = [col for col in df.columns if df[col].dtype == object]
            for col in text_columns:
                # Lọc các dòng chứa từ khóa lỗi phổ biến
                error_rows = df[df[col].astype(str).str.contains("error|exception|timeout|fail|slow", case=False, na=False)]
                if not error_rows.empty:
                    error_count += len(error_rows)
                    for _, row in error_rows.head(5).iterrows():  # Lấy tối đa 5 dòng log tiêu biểu làm bằng chứng
                        evidence.append({
                            "log_file": name,
                            "content": str(row.to_dict())
                        })

        if error_count > 0:
            summary = f"Detected {error_count} error/timeout log entries."
        else:
            summary = "No explicit error logs found in the given time window."

        return {
            "agent": self.name,
            "service": context.service,
            "log_tables": list(logs.keys()),
            "evidence": evidence,
            "summary": summary
        }