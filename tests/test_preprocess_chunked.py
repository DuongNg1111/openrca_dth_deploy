from datetime import datetime, timezone

from src.process_module.preprocess import preprocess_table


def _epoch(hour, minute):
    return int(
        datetime(2021, 3, 25, hour, minute, tzinfo=timezone.utc).timestamp()
    )


def test_preprocess_table_filters_large_files_chunk_by_chunk(tmp_path):
    csv_path = tmp_path / "metric_service.csv"
    csv_path.write_text(
        "timestamp,cmdb_id,kpi_name,value\n"
        f"{_epoch(8, 0)},order-service,cpu,10\n"
        f"{_epoch(9, 5)},order-service,cpu,90\n"
        f"{_epoch(10, 0)},order-service,cpu,10\n",
        encoding="utf-8",
    )
    window = {
        "start": datetime(2021, 3, 25, 9, 0),
        "end": datetime(2021, 3, 25, 9, 30),
    }

    result = preprocess_table(csv_path, window, chunksize=1)

    assert len(result) == 1
    assert result.iloc[0]["value"] == 90


def test_preprocess_table_applies_numeric_timestamp_offset(tmp_path):
    csv_path = tmp_path / "metric_service.csv"
    csv_path.write_text(
        "timestamp,cmdb_id,kpi_name,value\n"
        f"{_epoch(1, 5)},order-service,cpu,90\n",
        encoding="utf-8",
    )
    window = {
        "start": datetime(2021, 3, 25, 9, 0),
        "end": datetime(2021, 3, 25, 9, 30),
    }

    result = preprocess_table(
        csv_path,
        window,
        chunksize=1,
        timestamp_offset_hours=8,
    )

    assert len(result) == 1
    assert result.iloc[0]["timestamp"].hour == 9
