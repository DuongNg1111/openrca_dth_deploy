import pandas as pd

from types import SimpleNamespace
from datetime import datetime

from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import (
    build_investigation_context,
)
from src.schemas import TimeWindow


def test_step8_build_investigation_context():

    # ==========================================
    # 1. Fake telemetry (output from Step 6)
    # ==========================================

    telemetry = SimpleNamespace()

    telemetry.dataset = "cloudbed-2"


    telemetry.metrics = {
        "metric_service": pd.DataFrame(
            {
                "timestamp": [
                    1647771000000
                ],
                "cmdb_id": [
                    "productcatalogservice"
                ],
                "kpi_name": [
                    "rr"
                ],
                "value": [
                    10
                ]
            }
        )
    }


    telemetry.logs = {
        "log_proxy": pd.DataFrame(
            {
                "cmdb_id": [
                    "productcatalogservice"
                ],
                "message": [
                    "error"
                ]
            }
        )
    }


    telemetry.traces = {
        "trace_span": pd.DataFrame(
            {
                "cmdb_id": [
                    "productcatalogservice"
                ],
                "duration": [
                    100
                ]
            }
        )
    }



    # ==========================================
    # 2. Build service links (Step 7.1)
    # ==========================================

    service_links = build_service_links(
        telemetry
    )


    print("\nSERVICE LINKS")
    print(service_links)



    # ==========================================
    # 3. Fake parsed query
    # ==========================================

    parsed_query = SimpleNamespace()

    parsed_query.incident_time = datetime(
        2022,
        3,
        20,
        10,
        10
    )

    parsed_query.time_window = TimeWindow(
        start=datetime(
            2022,
            3,
            20,
            9,
            55
        ),
        end=datetime(
            2022,
            3,
            20,
            10,
            25
        )
    )



    # ==========================================
    # 4. Build Investigation Context (Step 7.2)
    # ==========================================

    contexts = build_investigation_context(
        telemetry,
        service_links,
        parsed_query,
    )


    print("\nCONTEXT")
    print(contexts)



    # ==========================================
    # 5. Assertions
    # ==========================================

    assert (
        "productcatalogservice"
        in contexts
    )


    context = contexts[
        "productcatalogservice"
    ]


    print("\nMETRICS:")
    print(context.metrics.keys())

    print("\nLOGS:")
    print(context.logs.keys())

    print("\nTRACES:")
    print(context.traces.keys())



    assert (
        "metric_service"
        in context.metrics
    )


    assert (
        "log_proxy"
        in context.logs
    )


    assert (
        "trace_span"
        in context.traces
    )