import json
from dataclasses import asdict
from datetime import datetime, timezone

import pytest

import src.full_pipeline as full_pipeline
from src.schemas import RawQuery


def _epoch(year, month, day, hour, minute):
    return int(datetime(year, month, day, hour, minute, tzinfo=timezone.utc).timestamp())


def _build_full_pipeline_fixture(
    tmp_path,
    *,
    dataset="cloudbed-1",
    empty=False,
    empty_modality=None,
    metric_value="100",
    extra_trace_duration=None,
):
    date_root = (
        tmp_path / "Market" / dataset / "telemetry" / "2021_03_25"
    )
    metric_dir = date_root / "metric"
    log_dir = date_root / "log"
    trace_dir = date_root / "trace"
    metric_dir.mkdir(parents=True)
    log_dir.mkdir()
    trace_dir.mkdir()

    metric_rows = ["timestamp,cmdb_id,kpi_name,value"]
    log_rows = ["timestamp,cmdb_id,message"]
    trace_rows = [
        "timestamp,cmdb_id,span_id,trace_id,duration,type,status_code,"
        "operation_name,parent_span"
    ]
    if not empty:
        timestamp = _epoch(2021, 3, 25, 9, 3)
        if empty_modality != "metric":
            metric_rows.append(
                f"{timestamp},order-service,disk_io_read,{metric_value}"
            )
        if empty_modality != "log":
            log_rows.append(f"{timestamp},order-service,disk queue warning")
        if empty_modality != "trace":
            trace_rows.append(
                f"{timestamp},order-service,span-1,trace-1,500,server,0,checkout,parent-1"
            )
            if extra_trace_duration is not None:
                trace_rows.append(
                    f"{timestamp},order-service,span-2,trace-2,{extra_trace_duration},"
                    "server,0,checkout,parent-1"
                )

    (metric_dir / "metric_service.csv").write_text(
        "\n".join(metric_rows) + "\n", encoding="utf-8"
    )
    (log_dir / "log_service.csv").write_text(
        "\n".join(log_rows) + "\n", encoding="utf-8"
    )
    (trace_dir / "trace_service.csv").write_text(
        "\n".join(trace_rows) + "\n", encoding="utf-8"
    )
    return tmp_path / "Market"


def _raw_query():
    return RawQuery(
        issue_key="LOCAL-1",
        incident_description="Orders are timing out",
        environment="Cloud A",
        affected_system="Order",
        incident_time="2021-03-25T09:03:00",
    )


def _forbid_live_calls(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("dry-run attempted a live or mutating call")

    for name in (
        "receive_query",
        "create_investigation",
        "insert_metrics",
        "insert_logs",
        "insert_traces",
        "insert_evidence",
        "get_investigation_evidence",
        "save_rca_result",
        "MetricAgent",
        "LogAgent",
        "TraceAgent",
        "ReasoningAgent",
    ):
        monkeypatch.setattr(full_pipeline, name, forbidden)


def test_dry_run_prepares_data_without_live_calls_or_writes(tmp_path, monkeypatch):
    data_root = _build_full_pipeline_fixture(tmp_path)
    _forbid_live_calls(monkeypatch)

    result = full_pipeline.run_pipeline(
        raw_query=_raw_query(),
        config={"system": "Market", "data_root": str(data_root)},
    )

    assert result["evidence_validation"].status == "COMPLETE"
    assert "order-service" in result["service_links"]


def test_python_api_requires_explicit_write_opt_in(tmp_path, monkeypatch):
    data_root = _build_full_pipeline_fixture(tmp_path)
    _forbid_live_calls(monkeypatch)

    result = full_pipeline.run_pipeline(
        raw_query=_raw_query(),
        config={"system": "Market", "data_root": str(data_root)},
    )

    assert result["evidence_validation"].status == "COMPLETE"


@pytest.mark.parametrize("invalid_dry_run", [None, 0, ""])
def test_python_api_rejects_non_boolean_write_authorization(
    invalid_dry_run,
    monkeypatch,
):
    _forbid_live_calls(monkeypatch)

    with pytest.raises(TypeError, match="actual bool"):
        full_pipeline.run_pipeline(
            raw_query=_raw_query(),
            config={},
            dry_run=invalid_dry_run,
        )


@pytest.mark.parametrize("invalid_run_agents", [None, 0, "false"])
def test_python_api_rejects_non_boolean_agent_authorization(
    invalid_run_agents,
    monkeypatch,
):
    _forbid_live_calls(monkeypatch)

    with pytest.raises(TypeError, match="only exact True permits agents"):
        full_pipeline.run_pipeline(
            raw_query=_raw_query(),
            config={},
            dry_run=False,
            run_agents=invalid_run_agents,
        )


def test_empty_preprocessed_data_fails_before_database_writes(tmp_path, monkeypatch):
    data_root = _build_full_pipeline_fixture(tmp_path, empty=True)
    _forbid_live_calls(monkeypatch)

    with pytest.raises(
        full_pipeline.EvidenceValidationError,
        match="before database writes.*telemetry records",
    ):
        full_pipeline.run_pipeline(
            raw_query=_raw_query(),
            config={"system": "Market", "data_root": str(data_root)},
            dry_run=False,
        )


def test_full_pipeline_rejects_a_missing_required_modality(tmp_path, monkeypatch):
    data_root = _build_full_pipeline_fixture(tmp_path, empty_modality="log")
    _forbid_live_calls(monkeypatch)

    with pytest.raises(
        full_pipeline.EvidenceValidationError,
        match="log telemetry records",
    ):
        full_pipeline.run_pipeline(
            raw_query=_raw_query(),
            config={"system": "Market", "data_root": str(data_root)},
        )


@pytest.mark.parametrize("invalid_value", ["garbage", "NaN", "inf", "-inf"])
def test_invalid_metric_values_fail_before_database_writes(
    tmp_path,
    monkeypatch,
    invalid_value,
):
    data_root = _build_full_pipeline_fixture(tmp_path, metric_value=invalid_value)
    _forbid_live_calls(monkeypatch)

    with pytest.raises(
        full_pipeline.EvidenceValidationError,
        match="non-numeric or non-finite",
    ):
        full_pipeline.run_pipeline(
            raw_query=_raw_query(),
            config={"system": "Market", "data_root": str(data_root)},
            dry_run=False,
        )


def test_mixed_valid_and_nan_trace_durations_fail_before_database_writes(
    tmp_path,
    monkeypatch,
):
    data_root = _build_full_pipeline_fixture(tmp_path, extra_trace_duration="NaN")
    _forbid_live_calls(monkeypatch)

    with pytest.raises(
        full_pipeline.EvidenceValidationError,
        match="PostgreSQL INTEGER contract",
    ):
        full_pipeline.run_pipeline(
            raw_query=_raw_query(),
            config={"system": "Market", "data_root": str(data_root)},
            dry_run=False,
        )


def test_cli_local_query_defaults_to_no_database_writes(tmp_path, monkeypatch, capsys):
    data_root = _build_full_pipeline_fixture(tmp_path)
    raw_query_path = tmp_path / "raw-query.json"
    raw_query_path.write_text(json.dumps(asdict(_raw_query())), encoding="utf-8")
    _forbid_live_calls(monkeypatch)

    full_pipeline.main(
        [
            "--raw-query-file",
            str(raw_query_path),
            "--data-root",
            str(data_root),
            "--dataset",
            "cloudbed-1",
            "--timestamp-offset-hours",
            "0",
        ]
    )

    assert '"database_writes": false' in capsys.readouterr().out


def test_cli_dataset_override_controls_full_pipeline_source(tmp_path, monkeypatch, capsys):
    data_root = _build_full_pipeline_fixture(tmp_path, dataset="review-fixture")
    raw_query_path = tmp_path / "raw-query.json"
    raw_query_path.write_text(json.dumps(asdict(_raw_query())), encoding="utf-8")
    _forbid_live_calls(monkeypatch)

    full_pipeline.main(
        [
            "--raw-query-file",
            str(raw_query_path),
            "--data-root",
            str(data_root),
            "--dataset",
            "review-fixture",
            "--timestamp-offset-hours",
            "0",
        ]
    )

    output = capsys.readouterr().out
    assert '"dataset": "review-fixture"' in output
    assert '"database_writes": false' in output
