from src.database.connection import get_connection
from src.process_module.service_links import build_service_links

import pandas as pd


ISSUE_KEY = "DEV-128"


# =====================================================
# STEP 1: GET INVESTIGATION
# =====================================================

def get_investigation(issue_key):

    conn = get_connection()

    query = """
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
        ORDER BY id DESC
        LIMIT 1;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(issue_key,)
    )

    conn.close()

    return df


# =====================================================
# STEP 2: GET RAW TELEMETRY
# =====================================================

def get_raw_telemetry(investigation_id):

    conn = get_connection()

    # -----------------------------
    # Metrics
    # -----------------------------

    metrics = pd.read_sql(
        """
        SELECT
            id,
            investigation_id,
            timestamp,
            cmdb_id,
            kpi_name,
            value
        FROM investigation_metrics
        WHERE investigation_id = %s
        ORDER BY timestamp;
        """,
        conn,
        params=(int(investigation_id),)
    )

    # -----------------------------
    # Logs
    # -----------------------------

    logs = pd.read_sql(
        """
        SELECT
            id,
            investigation_id,
            log_id,
            timestamp,
            cmdb_id,
            log_name,
            value
        FROM investigation_logs
        WHERE investigation_id = %s
        ORDER BY timestamp;
        """,
        conn,
        params=(int(investigation_id),)
    )

    # -----------------------------
    # Traces
    # -----------------------------

    traces = pd.read_sql(
        """
        SELECT
            id,
            investigation_id,
            timestamp,
            cmdb_id,
            span_id,
            trace_id,
            duration,
            type,
            status_code,
            operation_name,
            parent_span
        FROM investigation_traces
        WHERE investigation_id = %s
        ORDER BY timestamp;
        """,
        conn,
        params=(int(investigation_id),)
    )

    conn.close()

    return metrics, logs, traces


# =====================================================
# STEP 3: CREATE TELEMETRY OBJECT
# =====================================================

class Telemetry:

    def __init__(
        self,
        metrics,
        logs,
        traces
    ):

        self.metrics = metrics
        self.logs = logs
        self.traces = traces


# =====================================================
# MAIN TEST
# =====================================================

def main():

    print("\n")
    print("=" * 80)
    print("TEST SERVICE LINKS")
    print("=" * 80)

    # =================================================
    # 1. Investigation
    # =================================================

    investigation = get_investigation(
        ISSUE_KEY
    )

    print("\n[1] INVESTIGATION")

    print(investigation)

    if investigation.empty:

        print(
            f"\n❌ Investigation {ISSUE_KEY} not found."
        )

        return

    investigation_id = int(
        investigation.iloc[0]["id"]
    )

    print(
        "\nInvestigation ID:",
        investigation_id
    )

    # =================================================
    # 2. Get Telemetry
    # =================================================

    metrics, logs, traces = get_raw_telemetry(
        investigation_id
    )

    print("\n[2] RAW TELEMETRY")

    print(
        "\nMetrics rows:",
        len(metrics)
    )

    print(
        "Logs rows:",
        len(logs)
    )

    print(
        "Traces rows:",
        len(traces)
    )

    # =================================================
    # 3. Show Services
    # =================================================

    print("\n[3] RAW SERVICES")

    if not metrics.empty:

        print(
            "\nMetric services:"
        )

        print(
            metrics["cmdb_id"]
            .dropna()
            .unique()
            .tolist()
        )

    if not logs.empty:

        print(
            "\nLog services:"
        )

        print(
            logs["cmdb_id"]
            .dropna()
            .unique()
            .tolist()
        )

    if not traces.empty:

        print(
            "\nTrace services:"
        )

        print(
            traces["cmdb_id"]
            .dropna()
            .unique()
            .tolist()
        )

    # =================================================
    # 4. Build Telemetry Object
    # =================================================

    telemetry = Telemetry(

        metrics={
            "investigation_metrics": metrics
        },

        logs={
            "investigation_logs": logs
        },

        traces={
            "investigation_traces": traces
        }
    )

    # =================================================
    # 5. Build Service Links
    # =================================================

    print("\n[4] BUILD SERVICE LINKS")

    service_links = build_service_links(
        telemetry
    )

    # =================================================
    # 6. Result
    # =================================================

    print("\n[5] FINAL RESULT")

    print(
        "\nTotal services:",
        len(service_links)
    )

    for service, relation in service_links.items():

        print("\n----------------------------------------")

        print(
            "SERVICE:",
            service
        )

        print(
            "METRICS:",
            relation["metrics"]
        )

        print(
            "LOGS:",
            relation["logs"]
        )

        print(
            "TRACES:",
            relation["traces"]
        )

    # =================================================
    # 7. Basic Validation
    # =================================================

    print("\n[6] VALIDATION")

    if len(service_links) == 0:

        print(
            "❌ FAIL: No services found."
        )

    else:

        print(
            "✅ PASS: Service links created."
        )

    print("\n")
    print("=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":

    main()