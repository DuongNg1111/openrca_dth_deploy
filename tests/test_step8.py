from dataclasses import asdict
import pandas as pd

from src.jira.receive_query import receive_query

from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata

from src.process_module.preprocess import preprocess
from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import (
    build_investigation_context
)

from src.database.ready_call_db import (
    store_ready_call_data
)

from src.database.ready_call_query import (
    get_case,
    get_ready_call_data
)


# =====================================================
# Helper
# =====================================================

def print_title(title):

    print("\n" + "=" * 40)
    print(title)
    print("=" * 40)



def format_datetime(value):

    try:
        return pd.to_datetime(value).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except Exception:
        return value



# =====================================================
# MAIN PIPELINE
# =====================================================

def main():


    # =====================================================
    # STEP 1
    # =====================================================

    print_title(
        "STEP 1: RECEIVE USER QUERY"
    )


    issue_key = input(
        "Enter Jira Issue Key: "
    )


    raw_query = receive_query(
        issue_key
    )


    print("\nRaw Query")


    raw_data = asdict(raw_query)


    for key, value in raw_data.items():


        if key in [
            "incident_time",
            "created"
        ]:

            value = format_datetime(value)


        print(
            f"{key:<25}: {value}"
        )



    # =====================================================
    # STEP 2
    # =====================================================

    print_title(
        "STEP 2: VALIDATE QUERY"
    )


    validated = validate_query(
        raw_query
    )


    if not validated.is_valid:

        print(
            "Validation Failed"
        )

        print(
            validated.errors
        )

        return


    print(
        "Validation Passed"
    )



    # =====================================================
    # STEP 3
    # =====================================================

    print_title(
        "STEP 3: PARSE QUERY"
    )


    parsed_query = parse_query(
        raw_query
    )


    print("\nParsed Information")


    print(
        f"Keywords : {parsed_query.keywords}"
    )


    print(
        "\nInvestigation Window"
    )


    print(
        f"Start : {parsed_query.time_window.start.strftime('%Y-%m-%d %H:%M:%S')}"
    )


    print(
        f"End   : {parsed_query.time_window.end.strftime('%Y-%m-%d %H:%M:%S')}"
    )



    # =====================================================
    # STEP 4-5
    # =====================================================

    print_title(
        "STEP 4-5: LOAD TELEMETRY"
    )


    config = {

        "system": "Market",

        "data_root": "D:/"

    }


    data_source = connect_data_source(
        parsed_query,
        config
    )


    print(
        f"Data Source: {data_source}"
    )



    # =====================================================
    # STEP 6
    # =====================================================

    print_title(
        "STEP 6: LOAD METADATA"
    )


    metadata = load_metadata(
        data_source,
        parsed_query
    )


    print(
        f"Date Folder : {metadata.date}"
    )

    print(
        f"Metric Files: {metadata.metric.count}"
    )

    print(
        f"Log Files   : {metadata.log.count}"
    )

    print(
        f"Trace Files : {metadata.trace.count}"
    )

    print(
        f"Total Files : {metadata.total_files}"
    )



    # =====================================================
    # STEP 7
    # =====================================================

    print_title(
        "STEP 7: PREPROCESS"
    )


    preprocessed = preprocess(
        metadata,
        parsed_query
    )



    # =====================================================
    # STEP 8
    # =====================================================

    print_title(
        "STEP 8: BUILD INVESTIGATION CONTEXT"
    )


    service_links = build_service_links(
        preprocessed
    )


    contexts = build_investigation_context(
        preprocessed,
        service_links,
        parsed_query
    )

    from src.process_module.agents.log_agent import LogAgent
    from src.process_module.agents.metric_agent import MetricAgent
    from src.process_module.agents.trace_agent import TraceAgent
    from src.process_module.agents.reasoning_agent import ReasoningAgent


    print("\n========================================")
    print("STEP 9: AGENT TEST")
    print("========================================")


    # chọn 1 service để test trước

    context = contexts["shippingservice"]


    log_result = LogAgent().analyze(
        context
    )


    metric_result = MetricAgent().analyze(
        context
    )


    trace_result = TraceAgent().analyze(
        context
    )


    evidence = [

        log_result,
        metric_result,
        trace_result

    ]


    final_result = ReasoningAgent().analyze(
        evidence
    )


    print("\nLog Agent:")
    print(log_result)


    print("\nMetric Agent:")
    print(metric_result)


    print("\nTrace Agent:")
    print(trace_result)


    print("\nReasoning Agent:")
    print(final_result)

    print(
        f"Contexts Built: {len(contexts)}"
    )



    ready_db = store_ready_call_data(
        parsed_query,
        preprocessed,
        contexts
    )


    print(
        f"\nCases Stored    : {len(ready_db['cases'])}"
    )


    print(
        f"Services Stored : {len(ready_db['services'])}"
    )



    case = ready_db["cases"][0]


    print("\nCase Information")


    print(
        f"Issue Key   : {case.issue_key}"
    )

    print(
        f"Environment : {case.environment}"
    )

    print(
        f"Dataset     : {case.dataset}"
    )

    print(
        f"Incident    : {case.incident_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )



    # =====================================================
    # Query Result
    # =====================================================


    case = get_case(
        parsed_query.issue_key
    )


    records = get_ready_call_data(
        parsed_query.issue_key
    )


    print("\nQuery Result")


    print(
        f"Issue Key          : {case.issue_key}"
    )


    print(
        f"Dataset            : {case.dataset}"
    )


    print(
        f"Environment        : {case.environment}"
    )


    print(
        f"Contexts Returned  : {len(records)}"
    )


    for record in records:

        print("-" * 40)


        print(
            f"Service      : {record.service}"
        )


        print(
            f"Metric Files : {record.metric_files}"
        )


        print(
            f"Log Files    : {record.log_files}"
        )


        print(
            f"Trace Files  : {record.trace_files}"
        )


    print("-" * 40)



    # =====================================================
    # COMPLETED
    # =====================================================

    print_title(
        "PIPELINE COMPLETED"
    )



if __name__ == "__main__":

    main()