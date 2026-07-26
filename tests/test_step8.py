from dataclasses import asdict

from src.jira.receive_query import receive_query
from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata
from src.process_module.preprocess import preprocess
from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import build_investigation_context


def main():

    # =====================================================
    # STEP 1
    # =====================================================

    print("\n==============================")
    print(" STEP 1: RECEIVE USER QUERY ")
    print("==============================")

    issue_key = input("Enter Jira Issue Key: ")

    raw_query = receive_query(issue_key)

    print("\nRAW QUERY:")

    for key, value in asdict(raw_query).items():
        print(f"{key:<25}: {value}")

    # =====================================================
    # STEP 2
    # =====================================================

    print("\n==============================")
    print(" STEP 2: VALIDATE QUERY ")
    print("==============================")

    validated = validate_query(raw_query)

    if not validated.is_valid:
        print(validated.errors)
        return

    print(validated)

    # =====================================================
    # STEP 3
    # =====================================================

    print("\n==============================")
    print(" STEP 3: PARSE QUERY ")
    print("==============================")

    parsed_query = parse_query(raw_query)

    for key, value in asdict(parsed_query).items():
        print(f"{key:<25}: {value}")

    # =====================================================
    # STEP 4-5
    # =====================================================

    print("\n==============================")
    print(" STEP 4-5: LOAD TELEMETRY ")
    print("==============================")

    config = {
        "system": "Market",
        "data_root": "D:/"
    }

    data_source = connect_data_source(
        parsed_query,
        config
    )

    print(data_source)

    # =====================================================
    # STEP 6
    # =====================================================

    print("\n==============================")
    print(" STEP 6: LOAD METADATA ")
    print("==============================")

    metadata = load_metadata(
        data_source,
        parsed_query
    )

    print("Date Folder :", metadata.date)
    print("Metric Files:", metadata.metric.count)
    print("Log Files   :", metadata.log.count)
    print("Trace Files :", metadata.trace.count)
    print("Total Files :", metadata.total_files)

    # =====================================================
    # STEP 7
    # =====================================================

    print("\n==============================")
    print(" STEP 7: PREPROCESS ")
    print("==============================")

    preprocessed = preprocess(
        metadata,
        parsed_query
    )

    print("\nSTEP 7 COMPLETED")

    # from src.process_module.service_mapper import normalize_service_name

    # print("\n==============================")
    # print(" STEP 8 DEBUG ")
    # print("==============================")

    # # -----------------------------
    # # Metric services
    # # -----------------------------
    # metric_services = set()

    # for df in preprocessed.metrics.values():

    #     if "service" in df.columns:

    #         metric_services.update(
    #             df["service"]
    #             .dropna()
    #             .apply(normalize_service_name)
    #             .unique()
    #         )

    # # -----------------------------
    # # Log services
    # # -----------------------------
    # log_services = set()

    # for df in preprocessed.logs.values():

    #     if "cmdb_id" in df.columns:

    #         log_services.update(
    #             df["cmdb_id"]
    #             .dropna()
    #             .apply(normalize_service_name)
    #             .unique()
    #         )

    # # -----------------------------
    # # Trace services
    # # -----------------------------
    # trace_services = set()

    # for df in preprocessed.traces.values():

    #     if "cmdb_id" in df.columns:

    #         trace_services.update(
    #             df["cmdb_id"]
    #             .dropna()
    #             .apply(normalize_service_name)
    #             .unique()
    #         )

    # print("\nMetric Services")
    # print(sorted(metric_services))

    # print("\nLog Services")
    # print(sorted(log_services))

    # print("\nTrace Services")
    # print(sorted(trace_services))

    # =====================================================
    # STEP 8.2
    # =====================================================

    print("\n==============================")
    print(" STEP 8.2 SERVICE MAPPING ")
    print("==============================")

    service_links = build_service_links(
        preprocessed
    )

    for service, links in service_links.items():

        print(f"\nSERVICE: {service}")

        print(
            "Metrics:",
            sorted(links["metrics"])
        )

        print(
            "Logs:",
            sorted(links["logs"])
        )

        print(
            "Traces:",
            sorted(links["traces"])
        )

    # =====================================================
    # STEP 8.3
    # =====================================================

    print("\n==============================")
    print(" STEP 8.3 BUILD EVIDENCE BUNDLE ")
    print("==============================")

    contexts = build_investigation_context(
    preprocessed,
    service_links,
    parsed_query,
)

    for service, context in contexts.items():

        print(f"\nSERVICE: {context.service}")

        print(
            "Dataset       :",
            context.dataset
        )

        print(
            "Incident Time :",
            context.incident_time
        )
        print(
            "Time Window   :",
            f"{context.time_window.start} -> {context.time_window.end}"
        )

        print()

        print(
            "Metric Files:",
            list(context.metrics.keys())
        )

        print(
            "Log Files:",
            list(context.logs.keys())
        )

        print(
            "Trace Files:",
            list(context.traces.keys())
        )

        print()

        print(
            "Metric Rows:",
            sum(len(df) for df in context.metrics.values())
        )

        print(
            "Log Rows:",
            sum(len(df) for df in context.logs.values())
        )

        print(
            "Trace Rows:",
            sum(len(df) for df in context.traces.values())
        )

    print("\n==============================")
    print(" PIPELINE STEP 1-8 COMPLETED ")
    print("==============================")

if __name__ == "__main__":
        main()