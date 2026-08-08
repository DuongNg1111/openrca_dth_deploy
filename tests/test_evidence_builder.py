from datetime import datetime

import pandas as pd

from src.process_module.evidence_builder import build_investigation_context
from src.process_module.link_telemetry import build_service_links
from src.schemas import TimeWindow


class FakeTelemetry:
    dataset = "test_dataset"
    metrics = {
        "metric_service": pd.DataFrame(
            {"cmdb_id": ["cartservice-0", "frontend-0"], "value": [10.5, 20.5]}
        )
    }
    logs = {
        "log_service": pd.DataFrame(
            {"cmdb_id": ["cartservice-0", "currencyservice-1"]}
        )
    }
    traces = {
        "trace_service": pd.DataFrame(
            {"cmdb_id": ["frontend-0", "currencyservice-1"]}
        )
    }


class FakeParsedQuery:
    incident_time = datetime(2026, 8, 6, 10, 0, 0)
    time_window = TimeWindow(
        start=datetime(2026, 8, 6, 9, 45, 0),
        end=datetime(2026, 8, 6, 10, 15, 0),
    )


def test_evidence_builder_creates_database_backed_service_contexts():
    telemetry = FakeTelemetry()
    service_links = build_service_links(telemetry)

    contexts = build_investigation_context(
        telemetry=telemetry,
        service_links=service_links,
        parsed_query=FakeParsedQuery(),
        investigation_id=42,
    )

    assert set(contexts) == {"cartservice", "frontend", "currencyservice"}
    for service, context in contexts.items():
        assert context.service == service
        assert context.investigation_id == 42
        assert context.dataset == "test_dataset"
        assert context.time_window == FakeParsedQuery.time_window
        assert not hasattr(context, "metrics")
