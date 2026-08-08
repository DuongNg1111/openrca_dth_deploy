from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent

from src.database.repository import (
    insert_evidence,
    get_investigation_evidence,
    save_rca_result
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
        # 1. METRIC AGENT
        # =====================================================

        print("\nRunning Metric Agent...")

        metric_result = self.metric_agent.analyze(context)

        print(metric_result)


        # =====================================================
        # SAVE METRIC EVIDENCE
        # =====================================================

        for metric in metric_result.get(
            "anomalies",
            []
        ):

            insert_evidence(

                investigation_id=investigation_id,

                service=metric.get(
                    "service",
                    context.service
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


        # =====================================================
        # 2. LOG AGENT
        # =====================================================

        print("\nRunning Log Agent...")

        log_result = self.log_agent.analyze(context)

        print(log_result)


        # =====================================================
        # SAVE LOG EVIDENCE
        # =====================================================

        for log in log_result.get(
            "logs",
            []
        ):

            insert_evidence(

                investigation_id=investigation_id,

                service=log.get(
                    "service",
                    context.service
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


        # =====================================================
        # 3. TRACE AGENT
        # =====================================================

        print("\nRunning Trace Agent...")

        trace_result = self.trace_agent.analyze(context)

        print(trace_result)


        # =====================================================
        # SAVE TRACE EVIDENCE
        # =====================================================

        for trace in trace_result.get(
            "traces",
            []
        ):

            insert_evidence(

                investigation_id=investigation_id,

                service=trace.get(
                    "service",
                    context.service
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


        # =====================================================
        # 4. READ EVIDENCE FROM DATABASE
        # =====================================================

        print("\n========================================")
        print("LOADING EVIDENCE FROM DATABASE")
        print("========================================")

        evidence_df = get_investigation_evidence(
            investigation_id
        )


        print("\nEvidence Records:")

        print(evidence_df)


        # =====================================================
        # 5. BUILD EVIDENCE FOR REASONING AGENT
        # =====================================================

        evidence = {

            "metric": [],

            "log": [],

            "trace": []
        }


        for _, row in evidence_df.iterrows():

            evidence_type = row["evidence_type"]

            if evidence_type in evidence:

                evidence[evidence_type].append({

                    "service": row["service"],

                    "description": row["description"],

                    "score": row["score"]
                })


        print("\n========== REASONING EVIDENCE ==========")

        print(evidence)


        # =====================================================
        # 6. REASONING AGENT
        # =====================================================

        print("\nRunning Reasoning Agent...")


        final_result = self.reasoning_agent.analyze(

            context=context,

            evidence=evidence
        )


        print("\n========== RCA ==========")

        print(final_result)


        # =====================================================
        # 7. SAVE RCA RESULT
        # =====================================================

        if investigation_id is not None:

            save_rca_result(

                investigation_id=investigation_id,

                root_cause=final_result.get(
                    "root_cause",
                    ""
                ),

                confidence=final_result.get(
                    "confidence",
                    0
                ),

                explanation=final_result.get(
                    "explanation",
                    ""
                )
            )


            print("\nRCA Result Saved.")


        return final_result