from __future__ import annotations
from src.process_module.agents.base_agent import BaseAgent

class TraceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Trace Agent")

    def analyze(self, context):
        traces = context.traces
        evidence = []
        max_duration = 0

        for name, df in traces.items():
            if df.empty:
                continue

            if "duration" in df.columns:
                max_duration = max(max_duration, df["duration"].max() if not df["duration"].isna().all() else 0)
                # Lọc các trace có duration cao bất thường
                high_latency_spans = df[df["duration"] > df["duration"].quantile(0.95)] if len(df) > 1 else df
                for _, row in high_latency_spans.head(3).iterrows():
                    evidence.append({
                        "trace_file": name,
                        "span_info": str(row.to_dict())
                    })

        summary = f"Max trace duration observed: {max_duration} ms." if max_duration > 0 else "Trace analysis completed, no significant latency spikes."

        return {
            "agent": self.name,
            "service": context.service,
            "trace_tables": list(traces.keys()),
            "evidence": evidence,
            "summary": summary
        }