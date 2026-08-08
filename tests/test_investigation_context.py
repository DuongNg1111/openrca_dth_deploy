import pandas as pd

from src.database.connection import get_connection
from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import build_investigation_context
from src.process_module.service_mapper import normalize_service_name
from src.schemas import ParsedQuery, TimeWindow


ISSUE_KEY = "DEV-128"


def main():

    print("\n========================================")
    print("TEST INVESTIGATION CONTEXT")
    print("========================================")

    conn = get_connection()

    # =====================================================
    # 1. GET INVESTIGATION
    # =====================================================

    investigation = pd.read_sql(
        """
        SELECT
            id,
            issue_key,
            environment,
            affected_system,
            dataset,
            incident_time,
            window_start,
            window_end
        FROM investigations
        WHERE issue_key = %s
        """,
        conn,
        params=(ISSUE_KEY,),
    )

    if investigation.empty:
        raise RuntimeError(
            f"Investigation not found: {ISSUE_KEY}"
        )

    row = investigation.iloc[0]

    investigation_id = int(row["id"])

    print("\n[1] INVESTIGATION")
    print(investigation)

    print("\nInvestigation ID:", investigation_id)

    # =====================================================
    # 2. LOAD SAVED TELEMETRY
    # =====================================================

    metrics = pd.read_sql(
        """
        SELECT *
        FROM investigation_metrics
        WHERE investigation_id = %s
        """,
        conn,
        params=(investigation_id,),
    )

    logs = pd.read_sql(
        """
        SELECT *
        FROM investigation_logs
        WHERE investigation_id = %s
        """,
        conn,
        params=(investigation_id,),
    )

    traces = pd.read_sql(
        """
        SELECT *
        FROM investigation_traces
        WHERE investigation_id = %s
        """,
        conn,
        params=(investigation_id,),
    )

    print("\n[2] SAVED TELEMETRY")

    print("\nMetrics:", len(metrics))
    print(metrics.head())

    print("\nLogs:", len(logs))
    print(logs.head())

    print("\nTraces:", len(traces))
    print(traces.head())

    # =====================================================
    # 3. BUILD SIMPLE TELEMETRY OBJECT
    # =====================================================

    class Telemetry:
        pass

    telemetry = Telemetry()

    telemetry.dataset = row["dataset"]

    telemetry.metrics = {
        "metric_service": metrics
    }

    telemetry.logs = {
        "log_service": logs
    }

    telemetry.traces = {
        "trace_service": traces
    }

    # =====================================================
    # 4. BUILD SERVICE LINKS
    # =====================================================

    print("\n========================================")
    print("BUILD SERVICE LINKS")
    print("========================================")

    service_links = build_service_links(
        telemetry
    )

    # =====================================================
    # 5. BUILD PARSED QUERY
    # =====================================================

    parsed_query = ParsedQuery(
        issue_key=row["issue_key"],
        environment=row["environment"],
        incident_description="",
        affected_system=row["affected_system"],
        incident_time=row["incident_time"],
        additional_information="",
        time_window=TimeWindow(
            start=row["window_start"],
            end=row["window_end"],
        ),
        keywords=[],
    )

    # =====================================================
    # 6. BUILD INVESTIGATION CONTEXT
    # =====================================================

    print("\n========================================")
    print("BUILD INVESTIGATION CONTEXT")
    print("========================================")

    contexts = build_investigation_context(
        telemetry,
        service_links,
        parsed_query,
    )

    # =====================================================
    # 7. DEBUG RESULT
    # =====================================================

    print("\n========================================")
    print("CONTEXTS")
    print("========================================")

    print("Total contexts:", len(contexts))

    for service, context in contexts.items():

        print("\n----------------------------------------")
        print("SERVICE:", service)
        print("----------------------------------------")

        print(
            "Metrics:",
            list(context.metrics.keys())
        )

        print(
            "Logs:",
            list(context.logs.keys())
        )

        print(
            "Traces:",
            list(context.traces.keys())
        )

    # =====================================================
    # 8. BASIC VALIDATION
    # =====================================================

    print("\n========================================")
    print("VALIDATION")
    print("========================================")

    for service in contexts:

        assert service == normalize_service_name(service)

        print(
            "PASS:",
            service,
        )

    print("\n========================================")
    print("TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    main()