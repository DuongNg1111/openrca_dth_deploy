import pandas as pd
from types import SimpleNamespace

from src.process_module.link_telemetry import build_service_links


def main():

    print("\n========================================")
    print("TEST LINK TELEMETRY")
    print("========================================")

    # =================================================
    # MOCK METRICS
    # =================================================

    metrics = {
        "metric_service": pd.DataFrame({
            "cmdb_id": [
                "node-5.cartservice-1",
                "node-5.frontend-0",
                "node-5.cartservice-1",
            ],
            "kpi_name": [
                "container_spec_cpu_shares",
                "container_spec_cpu_shares",
                "container_spec_cpu_shares",
            ],
            "value": [
                409,
                204,
                409,
            ],
        })
    }

    # =================================================
    # MOCK LOGS
    # =================================================

    logs = {
        "log_service": pd.DataFrame({
            "cmdb_id": [
                "cartservice-1",
                "currencyservice-1",
            ],
            "log_name": [
                "log_cartservice-service_application",
                "log_currencyservice-service_application",
            ],
            "value": [
                "test cart log",
                "test currency log",
            ],
        })
    }

    # =================================================
    # MOCK TRACES
    # =================================================

    traces = {
        "trace_service": pd.DataFrame({
            "cmdb_id": [
                "frontend-2",
                "currencyservice-1",
            ],
            "trace_id": [
                "trace-001",
                "trace-002",
            ],
            "duration": [
                100,
                200,
            ],
        })
    }

    # =================================================
    # CREATE TELEMETRY OBJECT
    # =================================================

    telemetry = SimpleNamespace(
        metrics=metrics,
        logs=logs,
        traces=traces,
    )

    # =================================================
    # BUILD SERVICE LINKS
    # =================================================

    service_links = build_service_links(
        telemetry
    )

    # =================================================
    # PRINT RESULT
    # =================================================

    print("\n========================================")
    print("SERVICE LINKS")
    print("========================================")

    for service, relation in service_links.items():

        print("\nSERVICE:", service)

        print(
            "  Metrics:",
            relation["metrics"]
        )

        print(
            "  Logs:",
            relation["logs"]
        )

        print(
            "  Traces:",
            relation["traces"]
        )

    # =================================================
    # BASIC TESTS
    # =================================================

    assert isinstance(
        service_links,
        dict
    )

    assert len(service_links) > 0

    print("\n========================================")
    print("TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    main()