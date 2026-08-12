from datetime import datetime
from types import SimpleNamespace

import pandas as pd

from src.process_module.evidence_builder import build_investigation_context
from src.process_module.link_telemetry import build_service_links
from src.schemas import TimeWindow


def test_step8_builds_context_for_linked_service():
    telemetry = SimpleNamespace(
        dataset="cloudbed-2",
        metrics={
            "metric_service": pd.DataFrame(
                {"cmdb_id": ["productcatalogservice"], "value": [10]}
            )
        },
        logs={
            "log_proxy": pd.DataFrame(
                {"cmdb_id": ["productcatalogservice"], "message": ["error"]}
            )
        },
        traces={
            "trace_span": pd.DataFrame(
                {"cmdb_id": ["productcatalogservice"], "duration": [100]}
            )
        },
    )
    parsed_query = SimpleNamespace(
        incident_time=datetime(2022, 3, 20, 10, 10),
        time_window=TimeWindow(
            start=datetime(2022, 3, 20, 9, 55),
            end=datetime(2022, 3, 20, 10, 25),
        ),
    )

    contexts = build_investigation_context(
        telemetry,
        build_service_links(telemetry),
        parsed_query,
        investigation_id=84,
    )

    context = contexts["productcatalogservice"]
    assert context.investigation_id == 84
    assert context.dataset == "cloudbed-2"
    assert context.incident_time == parsed_query.incident_time
    assert context.time_window == parsed_query.time_window
