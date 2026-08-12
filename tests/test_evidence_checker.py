from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from src.process_module.evidence_checker import validate
from src.schemas import MetadataIndex, TelemetryMetadata


def test_complete_evidence_is_ready_for_reasoning():
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    telemetry = {"metric": [{"value": 99.0}], "log": [], "trace": []}

    result = validate(query, telemetry)

    assert result.status == "COMPLETE"
    assert result.ready_for_reasoning is True
    assert result.confidence == 1.0
    assert result.missing_evidence == []


def test_missing_context_and_telemetry_are_reported():
    result = validate({}, {"metric": [], "log": [], "trace": []})

    assert result.status == "INCOMPLETE"
    assert result.ready_for_reasoning is False
    assert "incident timestamp" in result.missing_evidence
    assert "telemetry records" in result.missing_evidence
    assert result.next_actions


def test_nested_empty_dataframes_are_not_telemetry_records():
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    telemetry = {
        "metrics": {"metric_service": pd.DataFrame()},
        "logs": {"log_service": pd.DataFrame()},
        "traces": {"trace_service": pd.DataFrame()},
    }

    result = validate(query, telemetry)

    assert result.status == "INCOMPLETE"
    assert "telemetry records" in result.missing_evidence


def test_zero_count_metadata_dataclasses_are_incomplete(tmp_path):
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    empty_metadata = TelemetryMetadata(folder=tmp_path, files=[], count=0)
    metadata = MetadataIndex(
        date="2021_03_25",
        metric=empty_metadata,
        log=TelemetryMetadata(folder=Path(tmp_path / "log"), files=[], count=0),
        trace=TelemetryMetadata(folder=Path(tmp_path / "trace"), files=[], count=0),
        total_files=0,
    )
    telemetry = SimpleNamespace(
        metrics={"metric_service": pd.DataFrame([{"value": 1.0}])},
        logs={},
        traces={},
    )

    result = validate(query, telemetry, metadata)

    assert result.status == "INCOMPLETE"
    assert "telemetry metadata" in result.missing_evidence


def test_nonempty_dataframe_must_match_persistence_schema():
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    telemetry = SimpleNamespace(
        metrics={
            "metric_service": pd.DataFrame(
                [
                    {
                        "timestamp": "2021-03-25 09:21:00",
                        "cmdb_id": "order-service",
                        "kpi_name": "cpu",
                        "value": 90,
                    }
                ]
            )
        },
        logs={},
        traces={"trace_service": pd.DataFrame([{"duration": 500}])},
    )

    result = validate(query, telemetry)

    assert result.status == "INCOMPLETE"
    assert any(item.startswith("trace schema missing") for item in result.missing_evidence)


def test_full_policy_requires_every_telemetry_modality():
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    telemetry = {
        "metrics": {
            "metric_service": pd.DataFrame(
                [
                    {
                        "timestamp": "2021-03-25 09:21:00",
                        "cmdb_id": "order-service",
                        "kpi_name": "cpu",
                        "value": 90,
                    }
                ]
            )
        },
        "logs": {},
        "traces": {},
    }

    result = validate(
        query,
        telemetry,
        required_modalities=("metric", "log", "trace"),
    )

    assert result.status == "INCOMPLETE"
    assert "log telemetry records" in result.missing_evidence
    assert "trace telemetry records" in result.missing_evidence


def test_nested_dataframe_with_all_null_required_values_is_unusable():
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    telemetry = {
        "metrics": [
            {
                "nested": pd.DataFrame(
                    [
                        {
                            "timestamp": "2021-03-25 09:21:00",
                            "cmdb_id": "order-service",
                            "kpi_name": None,
                            "value": None,
                        }
                    ]
                )
            }
        ]
    }

    result = validate(query, telemetry, required_modalities=("metric",))

    assert result.status == "INCOMPLETE"
    assert "metric schema has no usable populated rows" in result.missing_evidence


def test_full_policy_checks_metadata_per_modality(tmp_path):
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    frame = pd.DataFrame(
        [
            {
                "timestamp": "2021-03-25 09:21:00",
                "cmdb_id": "order-service",
                "kpi_name": "cpu",
                "value": 90,
            }
        ]
    )
    nonempty = TelemetryMetadata(folder=tmp_path, files=[tmp_path / "metric.csv"], count=1)
    empty = TelemetryMetadata(folder=tmp_path, files=[], count=0)
    metadata = MetadataIndex(
        date="2021_03_25",
        metric=nonempty,
        log=empty,
        trace=empty,
        total_files=1,
    )

    result = validate(
        query,
        {"metrics": {"metric": frame}, "logs": [1], "traces": [1]},
        metadata,
        required_modalities=("metric", "log", "trace"),
    )

    assert result.status == "INCOMPLETE"
    assert "log telemetry metadata" in result.missing_evidence
    assert "trace telemetry metadata" in result.missing_evidence


@pytest.mark.parametrize("invalid_value", [float("nan"), float("inf"), "garbage", True])
def test_metric_values_must_be_numeric_and_finite(invalid_value):
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    frame = pd.DataFrame(
        [
            {
                "timestamp": "2021-03-25 09:21:00",
                "cmdb_id": "order-service",
                "kpi_name": "cpu",
                "value": invalid_value,
            }
        ]
    )

    result = validate(
        query,
        {"metrics": {"metric": frame}},
        required_modalities=("metric",),
    )

    assert result.status == "INCOMPLETE"
    assert any(
        "non-numeric or non-finite" in issue
        for issue in result.missing_evidence
    )


@pytest.mark.parametrize(
    "invalid_duration",
    [float("nan"), float("inf"), -1, 1.5, 2_147_483_648, True],
)
def test_trace_durations_must_fit_the_persistence_contract(invalid_duration):
    query = SimpleNamespace(
        incident_time="2021-03-25 09:21:00",
        affected_system="order-service",
        incident_description="Orders time out",
    )
    trace_columns = {
        "timestamp": "2021-03-25 09:21:00",
        "cmdb_id": "order-service",
        "span_id": "span-1",
        "trace_id": "trace-1",
        "type": "server",
        "status_code": "0",
        "operation_name": "checkout",
        "parent_span": "parent-1",
    }
    frame = pd.DataFrame([
        {**trace_columns, "duration": 500},
        {**trace_columns, "span_id": "span-2", "duration": invalid_duration},
    ])

    result = validate(
        query,
        {"traces": {"trace": frame}},
        required_modalities=("trace",),
    )

    assert result.status == "INCOMPLETE"
    assert any(
        "PostgreSQL INTEGER contract" in issue
        for issue in result.missing_evidence
    )
