from __future__ import annotations
from src.process_module.agents.base_agent import BaseAgent

class MetricAgent(BaseAgent):
    def __init__(self):
        super().__init__("Metric Agent")

    def analyze(self, context):
        metrics = context.metrics
        evidence = []
        summaries = []

        for name, df in metrics.items():
            if df.empty or "value" not in df.columns:
                continue

            # Tính toán các chỉ số thống kê cơ bản trong cửa sổ thời gian sự cố
            max_val = df["value"].max()
            mean_val = df["value"].mean()

            # Lọc các dòng có giá trị vượt ngưỡng bất thường (ví dụ: cao hơn mean + 2*std hoặc top giá trị lớn nhất)
            if "kpi_name" in df.columns:
                for kpi in df["kpi_name"].unique():
                    kpi_df = df[df["kpi_name"] == kpi]
                    if not kpi_df.empty:
                        kpi_max = kpi_df["value"].max()
                        kpi_mean = kpi_df["value"].mean()
                        evidence.append({
                            "metric_file": name,
                            "kpi_name": kpi,
                            "max_value": float(kpi_max),
                            "mean_value": float(kpi_mean)
                        })
                        summaries.append(f"KPI '{kpi}' reached max value {kpi_max:.2f}")
            else:
                evidence.append({
                    "metric_file": name,
                    "max_value": float(max_val),
                    "mean_value": float(mean_val)
                })

        summary_text = ", ".join(summaries) if summaries else "No metric anomalies detected within the window."

        return {
            "agent": self.name,
            "service": context.service,
            "metric_tables": list(metrics.keys()),
            "evidence": evidence,
            "summary": summary_text
        }