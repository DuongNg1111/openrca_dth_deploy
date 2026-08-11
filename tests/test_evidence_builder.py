import pandas as pd
from datetime import datetime

from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import build_investigation_context


# =====================================================
# Fake Telemetry Object
# =====================================================

class FakeTelemetry:
    def __init__(self):
        self.dataset = "test_dataset"

        self.metrics = {
            "metric_service": pd.DataFrame({
                "cmdb_id": [
                    "cartservice-0",
                    "frontend-0",
                ],
                "timestamp": [
                    1000,
                    2000,
                ],
                "value": [
                    10.5,
                    20.5,
                ],
            })
        }

        self.logs = {
            "log_service": pd.DataFrame({
                "cmdb_id": [
                    "cartservice-0",
                    "currencyservice-1",
                ],
                "timestamp": [
                    1000,
                    2000,
                ],
                "message": [
                    "cart error",
                    "currency error",
                ],
            })
        }

        self.traces = {
            "trace_service": pd.DataFrame({
                "cmdb_id": [
                    "frontend-0",
                    "currencyservice-1",
                ],
                "timestamp": [
                    1000,
                    2000,
                ],
                "trace_id": [
                    "trace-001",
                    "trace-002",
                ],
            })
        }


# =====================================================
# Fake Parsed Query
# =====================================================

class FakeParsedQuery:
    def __init__(self):
        self.incident_time = datetime(
            2026,
            8,
            6,
            10,
            0,
            0,
        )

        self.time_window = None


# =====================================================
# TEST
# =====================================================

def test_evidence_builder():

    print("\n========================================")
    print("TEST EVIDENCE BUILDER")
    print("========================================")

    # -------------------------------------------------
    # 1. Create fake telemetry
    # -------------------------------------------------

    telemetry = FakeTelemetry()

    # -------------------------------------------------
    # 2. Build service links
    # -------------------------------------------------

    service_links = build_service_links(
        telemetry
    )

    print("\n========================================")
    print("SERVICE LINKS")
    print("========================================")

    for service, links in service_links.items():

        print(f"\nSERVICE: {service}")
        print("  Metrics:", links["metrics"])
        print("  Logs:", links["logs"])
        print("  Traces:", links["traces"])

    # -------------------------------------------------
    # 3. Create fake parsed query
    # -------------------------------------------------

    parsed_query = FakeParsedQuery()

    # -------------------------------------------------
    # 4. Build investigation contexts
    # -------------------------------------------------

    contexts = build_investigation_context(
        telemetry=telemetry,
        service_links=service_links,
        parsed_query=parsed_query,
    )

    # -------------------------------------------------
    # 5. Validate number of services
    # -------------------------------------------------

    expected_services = {
        "cartservice",
        "frontend",
        "currencyservice",
    }

    actual_services = set(contexts.keys())

    assert actual_services == expected_services, (
        f"Unexpected services.\n"
        f"Expected: {expected_services}\n"
        f"Actual: {actual_services}"
    )

    # -------------------------------------------------
    # 6. Validate cartservice
    # -------------------------------------------------

    cart_context = contexts["cartservice"]

    assert cart_context.service == "cartservice"

    assert set(
        cart_context.metrics.keys()
    ) == {"metric_service"}

    assert set(
        cart_context.logs.keys()
    ) == {"log_service"}

    assert set(
        cart_context.traces.keys()
    ) == set()

    # -------------------------------------------------
    # 7. Validate frontend
    # -------------------------------------------------

    frontend_context = contexts["frontend"]

    assert frontend_context.service == "frontend"

    assert set(
        frontend_context.metrics.keys()
    ) == {"metric_service"}

    assert set(
        frontend_context.logs.keys()
    ) == set()

    assert set(
        frontend_context.traces.keys()
    ) == {"trace_service"}

    # -------------------------------------------------
    # 8. Validate currencyservice
    # -------------------------------------------------

    currency_context = contexts["currencyservice"]

    assert currency_context.service == "currencyservice"

    assert set(
        currency_context.metrics.keys()
    ) == set()

    assert set(
        currency_context.logs.keys()
    ) == {"log_service"}

    assert set(
        currency_context.traces.keys()
    ) == {"trace_service"}

    # -------------------------------------------------
    # 9. Validate investigation metadata
    # -------------------------------------------------

    for service, context in contexts.items():

        assert context.dataset == "test_dataset"

        assert context.incident_time == (
            parsed_query.incident_time
        )

        assert context.time_window == (
            parsed_query.time_window
        )

    # -------------------------------------------------
    # 10. Validate DataFrames are preserved
    # -------------------------------------------------

    assert (
        contexts["cartservice"]
        .metrics["metric_service"]
        .shape[0]
        == 2
    )

    assert (
        contexts["cartservice"]
        .logs["log_service"]
        .shape[0]
        == 2
    )

    assert (
        contexts["frontend"]
        .traces["trace_service"]
        .shape[0]
        == 2
    )

    # -------------------------------------------------
    # PASS
    # -------------------------------------------------

    print("\n========================================")
    print("TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    test_evidence_builder()