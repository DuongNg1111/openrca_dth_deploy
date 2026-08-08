from dataclasses import asdict
import json
import pandas as pd

from src.jira.receive_query import receive_query

# from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata

from src.process_module.preprocess import preprocess
from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import (
    build_investigation_context,
)

from src.process_module.service_selector import (
    select_services,
)

# Import Agents
from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent
from src.database.repository import (
    create_investigation,
    insert_metrics,
    insert_logs,
    insert_traces,
    save_rca_result,
    insert_evidence
)


def run_pipeline(issue_key, run_agents=False):

    # =====================================================
    # STEP 1
    # =====================================================

    print("\n========================================")
    print("STEP 1: RECEIVE USER QUERY")
    print("========================================")


    raw_query = receive_query(issue_key)

    ...


    print("\nRaw Query")

    raw_data = asdict(raw_query)

    for key, value in raw_data.items():

        if key == "additional_information":
            continue

        print(
            f"{key:<25}: {value}"
        )
    # =====================================================
    # STEP 2
    # =====================================================

    print("\n========================================")
    print("STEP 2: PARSE QUERY")
    print("========================================")

    parsed_query = parse_query(
        raw_query
    )

    print("\nParsed Information")

    print(
        "Keywords :",
        parsed_query.keywords,
    )

    print("\nInvestigation Window")

    print(
        "Start :",
        parsed_query.time_window.start,
    )

    print(
        "End   :",
        parsed_query.time_window.end,
    )

        # =====================================================
    # STEP 3
    # =====================================================

    print("\n========================================")
    print("STEP 3-4: LOAD TELEMETRY")
    print("========================================")

    from src.config import load_config
    config = load_config() # Gọi hàm load_config để lấy đúng data_root đã cấu hình trong config.py

    data_source = connect_data_source(
        parsed_query,
        config,
    )

    print("Data Source:", data_source)

    # =====================================================
    # STEP 5
    # =====================================================

    print("\n========================================")
    print("STEP 5: LOAD METADATA")
    print("========================================")

    metadata = load_metadata(
        data_source,
        parsed_query,
    )

    print("Date Folder :", metadata.date)
    print("Metric Files:", metadata.metric.count)
    print("Log Files   :", metadata.log.count)
    print("Trace Files :", metadata.trace.count)
    print("Total Files :", metadata.total_files)

    # =====================================================
    # STEP 6
    # =====================================================

    print("\n========================================")
    print("STEP 6: PREPROCESS")
    print("========================================")

    preprocessed = preprocess(
        metadata,
        parsed_query,
    )

    print("\nPreprocess Completed")

    # =====================================================
    # STEP 7
    # =====================================================

    print("\n========================================")
    print("STEP 7: BUILD READY-TO-CALL DATABASE")
    print("========================================")


    # =====================================================
    # STEP 7.1: BUILD SERVICE LINKS
    # =====================================================

    print("\n========================================")
    print("STEP 7.1: BUILD SERVICE LINKS")
    print("========================================")


    service_links = build_service_links(
        preprocessed
    )


    print(
        "Service Links Built:",
        len(service_links)
    )


    # =====================================================
    # STEP 7.2: PREPARE AGENT CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 7.2: PREPARE AGENT CONTEXT")
    print("========================================")


    print(
        "Ready-To-Call Context Prepared"
    )



    # =====================================================
    # STEP 7.3: SAVE INVESTIGATION
    # =====================================================

    print("\n========================================")
    print("STEP 7.3: SAVE INVESTIGATION")
    print("========================================")


    investigation_id = create_investigation(
        issue_key=parsed_query.issue_key,
        environment=parsed_query.environment,
        affected_system=parsed_query.affected_system,
        dataset=preprocessed.dataset,
        incident_time=parsed_query.incident_time,
        window_start=parsed_query.time_window.start,
        window_end=parsed_query.time_window.end,
        incident_description=raw_query.incident_description,
        reporter=raw_query.reporter,
        reporter_email="",
    )



    print(
        "Investigation ID:",
        investigation_id
    )



    # =====================================================
    # STEP 7.4: SAVE METRICS
    # =====================================================

    print("\n========================================")
    print("STEP 7.4: SAVE METRICS")
    print("========================================")


    for df in preprocessed.metrics.values():

        insert_metrics(
            investigation_id,
            df
        )


    print(
        "Metrics Saved"
    )



    # =====================================================
    # STEP 7.5: SAVE LOGS
    # =====================================================

    print("\n========================================")
    print("STEP 7.5: SAVE LOGS")
    # =====================================================


    for df in preprocessed.logs.values():

        insert_logs(
            investigation_id,
            df
        )


    print(
        "Logs Saved"
    )



    # =====================================================
    # STEP 7.6: SAVE TRACES
    # =====================================================

    print("\n========================================")
    print("STEP 7.6: SAVE TRACES")
    print("========================================")


    for df in preprocessed.traces.values():

        insert_traces(
            investigation_id,
            df
        )


    print(
        "Traces Saved"
    )

    # =====================================================
    # STEP 7.7: BUILD INVESTIGATION CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 7.7: BUILD INVESTIGATION CONTEXT")
    print("========================================")

    contexts = build_investigation_context(
        preprocessed,
        service_links,
        parsed_query,
        investigation_id=investigation_id,
    )

    print(
        "Contexts Built:",
        len(contexts)
    )
    # =====================================================
    # STEP 8
    # =====================================================

    print("\n========================================")
    print("STEP 8: SERVICE SELECTION")
    print("========================================")

    selected_contexts = select_services(
        parsed_query,
        contexts,
    )

    print("Affected System :", parsed_query.affected_system)
    print("Keywords        :", parsed_query.keywords)

    print("\nSelected Services :", len(selected_contexts))

    for service in selected_contexts.values():

        print("-", service.service)

    if not run_agents:

        print("\n========================================")
        print("PIPELINE STOPPED BEFORE AGENTS")
        print("READY FOR AGENT ANALYSIS")
        print("========================================")

        return selected_contexts

    # =====================================================
# STEP 9: MULTI-AGENT ANALYSIS
# =====================================================

print("\n========================================")
print("STEP 9: MULTI-AGENT ANALYSIS")
print("========================================")


metric_agent = MetricAgent()
log_agent = LogAgent()
trace_agent = TraceAgent()

reasoning_agent = ReasoningAgent()


# =====================================================
# DEBUG CONTEXT
# =====================================================

print("\n==============================")
print("SELECTED CONTEXTS DEBUG")
print("==============================")


for service, context in selected_contexts.items():

    print("\nSERVICE:", service)
    print(
        "INVESTIGATION ID:",
        context.investigation_id
    )



# =====================================================
# RUN AGENTS
# =====================================================

for context in selected_contexts.values():

    print("\n----------------------------------------")
    print("SERVICE:", context.service)
    print(
        "INVESTIGATION ID:",
        context.investigation_id
    )
    print("----------------------------------------")


    # =================================================
    # 1. METRIC AGENT
    # =================================================

    print("\nRunning Metric Agent...")

    metric_result = metric_agent.analyze(
        context
    )

    print(
        "Metric Agent completed."
    )


    # =================================================
    # SAVE METRIC EVIDENCE
    # =================================================

    for metric in metric_result.get(
        "anomalies",
        []
    ):

        insert_evidence(
            investigation_id=context.investigation_id,
            service=context.service,
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


    # =================================================
    # 2. LOG AGENT
    # =================================================

    print("\nRunning Log Agent...")

    log_result = log_agent.analyze(
        context
    )

    print(
        "Log Agent completed."
    )


    # =================================================
    # SAVE LOG EVIDENCE
    # =================================================

    for log in log_result.get(
        "errors",
        []
    ):

        insert_evidence(
            investigation_id=context.investigation_id,
            service=context.service,
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


    # =================================================
    # 3. TRACE AGENT
    # =================================================

    print("\nRunning Trace Agent...")

    trace_result = trace_agent.analyze(
        context
    )

    print(
        "Trace Agent completed."
    )


    # =================================================
    # SAVE TRACE EVIDENCE
    # =================================================

    for trace in trace_result.get(
        "traces",
        []
    ):

        insert_evidence(
            investigation_id=context.investigation_id,
            service=context.service,
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


    # =================================================
    # 4. REASONING AGENT
    # READ FROM evidence_records
    # =================================================

    print("\nRunning Reasoning Agent...")


    final_output = reasoning_agent.analyze(
        context
    )


    print(
        "Reasoning Agent completed."
    )


    # =================================================
    # SAVE RCA RESULT
    # =================================================

    save_rca_result(
        investigation_id=context.investigation_id,
        root_cause=final_output.get(
            "reason",
            "unknown"
        ),
        confidence=float(
            final_output.get(
                "confidence",
                0.0
            )
        ),
        explanation=final_output.get(
            "reasoning",
            ""
        )
    )


    # =================================================
    # DEBUG FINAL OUTPUT
    # =================================================

    print("\n========================================")
    print("FINAL RCA OUTPUT")
    print("========================================")


    print(
        json.dumps(
            final_output,
            indent=4,
            default=str
        )
    )


# =====================================================
# FINISH
# =====================================================

print("\n========================================")
print("PIPELINE COMPLETED")
print("========================================")