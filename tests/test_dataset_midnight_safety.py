from datetime import datetime
from types import SimpleNamespace

import pytest

from src.input_module.metadata_loader import build_metadata_index
from src.input_module.telemetry_loader import connect_data_source
from src.process_module.preprocess import preprocess
from src.schemas import TimeWindow


def _parsed_query(environment="Cloud A", *, start=None, end=None):
    start = start or datetime(2022, 3, 20, 9, 0)
    end = end or datetime(2022, 3, 20, 9, 30)
    return SimpleNamespace(
        environment=environment,
        incident_time=start + (end - start) / 2,
        time_window=TimeWindow(start=start, end=end),
    )


def _write_day(telemetry_root, day, timestamp):
    date_folder = telemetry_root / day
    for modality in ("metric", "log", "trace"):
        (date_folder / modality).mkdir(parents=True)

    (date_folder / "metric" / "metric_service.csv").write_text(
        "timestamp,cmdb_id,kpi_name,value\n"
        f"{timestamp},shippingservice-1,cpu,42\n",
        encoding="utf-8",
    )
    (date_folder / "log" / "log_service.csv").write_text(
        "timestamp,cmdb_id,value\n"
        f"{timestamp},shippingservice-1,warning\n",
        encoding="utf-8",
    )
    (date_folder / "trace" / "trace_span.csv").write_text(
        "timestamp,cmdb_id,span_id,trace_id,duration,type,status_code,"
        "operation_name,parent_span\n"
        f"{timestamp},shippingservice-1,span,trace,1,SERVER,200,ship,parent\n",
        encoding="utf-8",
    )


def test_environment_mapping_is_preserved_without_explicit_override(tmp_path):
    expected = tmp_path / "cloudbed-2" / "telemetry"
    expected.mkdir(parents=True)

    result = connect_data_source(
        _parsed_query("Cloud B"),
        {
            "system": "Market",
            "data_root": str(tmp_path),
            # A configured default is not an explicit operator override.
            "dataset": "cloudbed-1",
        },
    )

    assert result == expected


def test_explicit_dataset_override_takes_precedence(tmp_path):
    expected = tmp_path / "review-fixture" / "telemetry"
    expected.mkdir(parents=True)

    result = connect_data_source(
        _parsed_query("not-in-the-environment-map"),
        {
            "system": "Market",
            "data_root": str(tmp_path),
            "dataset_override": "review-fixture",
        },
    )

    assert result == expected


def test_configured_data_root_never_silently_falls_back_to_cwd(tmp_path, monkeypatch):
    configured_root = tmp_path / "configured-but-missing"
    fallback = tmp_path / "data" / "Market" / "cloudbed-1" / "telemetry"
    fallback.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match=str(configured_root)):
        connect_data_source(
            _parsed_query(),
            {"system": "Market", "data_root": str(configured_root)},
        )


@pytest.mark.parametrize("override", ["../cloudbed-1", "/tmp/data", "bed/two", " bed"])
def test_dataset_override_rejects_unsafe_folder_names(tmp_path, override):
    with pytest.raises(ValueError, match="single safe folder name"):
        connect_data_source(
            _parsed_query(),
            {
                "system": "Market",
                "data_root": str(tmp_path),
                "dataset_override": override,
            },
        )


def test_metadata_and_preprocess_keep_both_sides_of_midnight(tmp_path):
    telemetry_root = tmp_path / "cloudbed-1" / "telemetry"
    _write_day(telemetry_root, "2022_03_20", "2022-03-20 23:58:00")
    _write_day(telemetry_root, "2022_03_21", "2022-03-21 00:02:00")
    parsed_query = _parsed_query(
        start=datetime(2022, 3, 20, 23, 55),
        end=datetime(2022, 3, 21, 0, 5),
    )

    metadata = build_metadata_index(telemetry_root, parsed_query)
    prepared = preprocess(metadata, parsed_query)

    assert metadata.date == "2022_03_20,2022_03_21"
    assert metadata.metric.count == 2
    assert metadata.log.count == 2
    assert metadata.trace.count == 2
    assert metadata.total_files == 6
    assert len(prepared.metrics["metric_service"]) == 2
    assert len(prepared.logs["log_service"]) == 2
    assert len(prepared.traces["trace_span"]) == 2


def test_metadata_fails_when_an_adjacent_date_folder_is_missing(tmp_path):
    telemetry_root = tmp_path / "cloudbed-1" / "telemetry"
    _write_day(telemetry_root, "2022_03_20", "2022-03-20 23:58:00")
    parsed_query = _parsed_query(
        start=datetime(2022, 3, 20, 23, 55),
        end=datetime(2022, 3, 21, 0, 5),
    )

    with pytest.raises(FileNotFoundError, match="2022_03_21"):
        build_metadata_index(telemetry_root, parsed_query)
