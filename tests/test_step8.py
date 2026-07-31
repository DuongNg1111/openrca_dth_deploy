import pandas as pd
from datetime import datetime

from src.process_module.evidence_builder import (
    build_investigation_context,
)

from src.schemas import TimeWindow


# ======================================================
# MOCK TELEMETRY
# ======================================================

class MockTelemetry:

    dataset = "cloudbed-1"

    metrics = {
        "metric_service": pd.DataFrame(
            {
                "timestamp": [1647855000000],
                "service": ["productcatalogservice"],
                "value": [100],
            }
        )
    }

    logs = {
        "log_service": pd.DataFrame(
            {
                "timestamp": [1647855000000],
                "message": ["error"]
            }
        )
    }

    traces = {
        "trace_span": pd.DataFrame(
            {
                "trace_id": ["abc"],
                "duration": [200]
            }
        )
    }


# ======================================================
# MOCK QUERY
# ======================================================

class MockQuery:

    incident_time = datetime(
        2022,
        3,
        21,
        9,
        30
    )

    time_window = TimeWindow(
        start=datetime(
            2022,
            3,
            21,
            9,
            15
        ),
        end=datetime(
            2022,
            3,
            21,
            9,
            45
        )
    )


# ======================================================
# STEP 8.3 TEST
# ======================================================

def test_build_investigation_context():

    telemetry = MockTelemetry()

    service_links = {

        "productcatalogservice": {

            "metrics": [
                "metric_service"
            ],

            "logs": [
                "log_service"
            ],

            "traces": [
                "trace_span"
            ]
        }
    }


    contexts = build_investigation_context(
        telemetry,
        service_links,
        MockQuery()
    )


    # -----------------------------
    # Check service exists
    # -----------------------------

    assert (
        "productcatalogservice"
        in contexts
    )


    context = contexts[
        "productcatalogservice"
    ]


    # -----------------------------
    # Check metrics
    # -----------------------------

    assert (
        "metric_service"
        in context.metrics
    )

    assert isinstance(
        context.metrics["metric_service"],
        pd.DataFrame
    )


    # -----------------------------
    # Check logs
    # -----------------------------

    assert (
        "log_service"
        in context.logs
    )


    # -----------------------------
    # Check traces
    # -----------------------------

    assert (
        "trace_span"
        in context.traces
    )


    # -----------------------------
    # Debug output
    # -----------------------------

    print("==============================")
    print("SERVICE:", context.service)
    print(
        "METRICS:",
        context.metrics.keys()
    )
    print(
        "LOGS:",
        context.logs.keys()
    )
    print(
        "TRACES:",
        context.traces.keys()
    )