from dataclasses import asdict
import json

from src.jira.receive_query import receive_query

from src.input_module.validate_query import validate_query
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

from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent
from src.database.repository import (
    create_investigation,
    insert_metrics,
    insert_logs,
    insert_traces,
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
    print("STEP 2: VALIDATE QUERY")
    print("========================================")

    validation = validate_query(
        raw_query
    )

    if not validation.is_valid:

        print("\nValidation Failed")

        for error in validation.errors:

            print("-", error)

        print("\n========================================")
        print("PIPELINE STOPPED")
        print("========================================")

        return

    print("Validation Passed")

    # =====================================================
    # STEP 3
    # =====================================================

    print("\n========================================")
    print("STEP 3: PARSE QUERY")
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
    # STEP 4-5
    # =====================================================

    print("\n========================================")
    print("STEP 4-5: LOAD TELEMETRY")
    print("========================================")

    from src.config import load_config
    config = load_config() # Gọi hàm load_config để lấy đúng data_root đã cấu hình trong config.py

    data_source = connect_data_source(
        parsed_query,
        config,
    )

    print("Data Source:", data_source)

    # =====================================================
    # STEP 6
    # =====================================================

    print("\n========================================")
    print("STEP 6: LOAD METADATA")
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
    # STEP 7
    # =====================================================

    print("\n========================================")
    print("STEP 7: PREPROCESS")
    print("========================================")

    preprocessed = preprocess(
        metadata,
        parsed_query,
    )

    print("\nPreprocess Completed")

    # =====================================================
    # STEP 8
    # =====================================================

    print("\n========================================")
    print("STEP 8: BUILD READY-TO-CALL DATABASE")
    print("========================================")


    # =====================================================
    # STEP 8.1: BUILD SERVICE LINKS
    # =====================================================

    print("\n========================================")
    print("STEP 8.1: BUILD SERVICE LINKS")
    print("========================================")


    service_links = build_service_links(
        preprocessed
    )


    print(
        "Service Links Built:",
        len(service_links)
    )



    # =====================================================
    # STEP 8.2: BUILD INVESTIGATION CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 8.2: BUILD INVESTIGATION CONTEXT")
    print("========================================")


    contexts = build_investigation_context(
        preprocessed,
        service_links,
        parsed_query,
    )


    print(
        "Contexts Built:",
        len(contexts)
    )



    # =====================================================
    # STEP 8.3: PREPARE AGENT CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 8.3: PREPARE AGENT CONTEXT")
    print("========================================")


    print(
        "Ready-To-Call Context Prepared"
    )



    # =====================================================
    # STEP 8.4: SAVE INVESTIGATION
    # =====================================================

    print("\n========================================")
    print("STEP 8.4: SAVE INVESTIGATION")
    print("========================================")


    investigation_id = create_investigation(
        issue_key=parsed_query.issue_key,
        environment=parsed_query.environment,
        dataset=preprocessed.dataset,
        incident_time=parsed_query.incident_time,
        window_start=parsed_query.time_window.start,
        window_end=parsed_query.time_window.end,
        incident_description=raw_query.incident_description,
    )


    print(
        "Investigation ID:",
        investigation_id
    )



    # =====================================================
    # STEP 8.5: SAVE METRICS
    # =====================================================

    print("\n========================================")
    print("STEP 8.5: SAVE METRICS")
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
    # STEP 8.6: SAVE LOGS
    # =====================================================

    print("\n========================================")
    print("STEP 8.6: SAVE LOGS")
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
    # STEP 8.7: SAVE TRACES
    # =====================================================

    print("\n========================================")
    print("STEP 8.7: SAVE TRACES")
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
    # STEP 9
    # =====================================================

    print("\n========================================")
    print("STEP 9: SERVICE SELECTION")
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
    # STEP 10
    # =====================================================

    print("\n========================================")
    print("STEP 10: MULTI-AGENT ANALYSIS")
    print("========================================")

    metric_agent = MetricAgent()

    log_agent = LogAgent()

    trace_agent = TraceAgent()

    reasoning_agent = ReasoningAgent()

    for context in selected_contexts.values():
        print("\n----------------------------------------")
        print("SERVICE :", context.service)
        print("----------------------------------------")

        metric_result = metric_agent.analyze(context)
        log_result = log_agent.analyze(context)
        trace_result = trace_agent.analyze(context)

        # Chỉ gọi 1 lần với đầy đủ context và kết quả 3 agent
        final_output = reasoning_agent.analyze(
            context,
            metric_result,
            log_result,
            trace_result
        )

        print("\nMetric Agent")
        print(metric_result)

        print("\nLog Agent")
        print(log_result)

        print("\nTrace Agent")
        print(trace_result)

        print("\nFinal Output JSON format:")
        print(json.dumps(final_output, indent=4, default=str))

    # =====================================================
    # FINISH
    # =====================================================

    print("\n========================================")
    print("PIPELINE COMPLETED")
    print("========================================")


if __name__ == "__main__":

    issue_key = input("Enter Jira Issue Key: ")

    run_pipeline(
        issue_key,
        run_agents=True
    )