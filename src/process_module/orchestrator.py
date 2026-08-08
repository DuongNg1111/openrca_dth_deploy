from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent

from src.database.repository import (
    insert_evidence,
    get_investigation_evidence,
    save_rca_result,
)


class ProcessOrchestrator:

    def __init__(self):

        self.metric_agent = MetricAgent()
        self.log_agent = LogAgent()
        self.trace_agent = TraceAgent()
        self.reasoning_agent = ReasoningAgent()

    def run(
        self,
        context,
        investigation_id=None
    ):

        print("\n========== PROCESS MODULE ==========")

        # =====================================================
        # VALIDATE INVESTIGATION ID
        # =====================================================

        if investigation_id is None:

            investigation_id = getattr(
                context,
                "investigation_id",
                None
            )

        if investigation_id is None:

            raise ValueError(
                "investigation_id is required for ProcessOrchestrator."
            )

        print(
            f"\nInvestigation ID: {investigation_id}"
        )

        # =====================================================
        # 1. METRIC AGENT
        # =====================================================

        print("\n========================================")
        print("1. METRIC AGENT")
        print("========================================")

        metric_result = self.metric_agent.analyze(
            context
        )

        print("\nMetric Result:")
        print(metric_result)

        # =====================================================
        # SAVE METRIC EVIDENCE
        # =====================================================

        print("\nSaving Metric Evidence...")

        metric_evidence_count = 0

        for metric in metric_result.get(
            "anomalies",
            []
        ):

            insert_evidence(

                investigation_id=investigation_id,

                service=metric.get(
                    "service",
                    getattr(
                        context,
                        "service",
                        "unknown"
                    )
                ),

                evidence_type="metric",

                description=metric.get(
                    "description",
                    ""
                ),

                score=float(
                    metric.get(
                        "value",
                        0.0
                    )
                )
            )

            metric_evidence_count += 1

        print(
            f"Metric evidence saved: "
            f"{metric_evidence_count}"
        )

        # =====================================================
        # 2. LOG AGENT
        # =====================================================

        print("\n========================================")
        print("2. LOG AGENT")
        print("========================================")

        log_result = self.log_agent.analyze(
            context
        )

        print("\nLog Result:")
        print(log_result)

        # =====================================================
        # SAVE LOG EVIDENCE
        # =====================================================

        print("\nSaving Log Evidence...")

        log_evidence_count = 0

        for log in log_result.get(
            "logs",
            []
        ):

            insert_evidence(

                investigation_id=investigation_id,

                service=log.get(
                    "service",
                    getattr(
                        context,
                        "service",
                        "unknown"
                    )
                ),

                evidence_type="log",

                description=log.get(
                    "message",
                    ""
                ),

                score=float(
                    log.get(
                        "count",
                        0.0
                    )
                )
            )

            log_evidence_count += 1

        print(
            f"Log evidence saved: "
            f"{log_evidence_count}"
        )

        # =====================================================
        # 3. TRACE AGENT
        # =====================================================

        print("\n========================================")
        print("3. TRACE AGENT")
        print("========================================")

        trace_result = self.trace_agent.analyze(
            context
        )

        print("\nTrace Result:")
        print(trace_result)

        # =====================================================
        # SAVE TRACE EVIDENCE
        # =====================================================

        print("\nSaving Trace Evidence...")

        trace_evidence_count = 0

        for trace in trace_result.get(
            "traces",
            []
        ):

            insert_evidence(

                investigation_id=investigation_id,

                service=trace.get(
                    "service",
                    getattr(
                        context,
                        "service",
                        "unknown"
                    )
                ),

                evidence_type="trace",

                description=trace.get(
                    "description",
                    ""
                ),

                score=float(
                    trace.get(
                        "latency_ms",
                        0.0
                    )
                )
            )

            trace_evidence_count += 1

        print(
            f"Trace evidence saved: "
            f"{trace_evidence_count}"
        )

        # =====================================================
        # 4. LOAD EVIDENCE FROM DATABASE
        # =====================================================

        print("\n========================================")
        print("4. LOAD EVIDENCE FROM DATABASE")
        print("========================================")

        evidence_df = get_investigation_evidence(
            investigation_id
        )

        print("\nEvidence loaded from database:")

        print(
            evidence_df
        )

        # =====================================================
        # CHECK EVIDENCE
        # =====================================================

        if evidence_df is None or evidence_df.empty:

            print(
                "\nWARNING: No evidence found."
            )

        else:

            print(
                f"\nTotal evidence records: "
                f"{len(evidence_df)}"
            )

        # =====================================================
        # 5. REASONING AGENT
        # =====================================================

        print("\n========================================")
        print("5. REASONING AGENT")
        print("========================================")

        final_result = self.reasoning_agent.analyze(

            context,

            evidence_df

        )

        print("\nReasoning Result:")
        print(final_result)

        # =====================================================
        # 6. SAVE RCA RESULT
        # =====================================================

        print("\n========================================")
        print("6. SAVE RCA RESULT")
        print("========================================")

        save_rca_result(

            investigation_id=investigation_id,

            root_cause=final_result.get(
                "root_cause",
                final_result.get(
                    "reason",
                    ""
                )
            ),

            confidence=final_result.get(
                "confidence",
                0
            ),

            explanation=final_result.get(
                "explanation",
                final_result.get(
                    "reasoning",
                    ""
                )
            )
        )

        print(
            "\nRCA Result Saved Successfully."
        )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        print("\n========================================")
        print("FINAL RCA")
        print("========================================")

        print(
            final_result
        )

        return final_result