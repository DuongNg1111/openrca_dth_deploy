from datetime import datetime, timezone

from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import load
from src.pipeline import run


def _build_market_fixture(tmp_path):
    date_root = (
        tmp_path / "Market" / "cloudbed-1" / "telemetry" / "2021_03_25"
    )
    metric_dir = date_root / "metric"
    log_dir = date_root / "log"
    trace_dir = date_root / "trace"
    metric_dir.mkdir(parents=True)
    log_dir.mkdir()
    trace_dir.mkdir()

    rows = ["timestamp,service,disk_io_read,cpu"]
    for minute in range(6):
        timestamp = f"2021-03-25 09:0{minute}:00"
        order_disk = 10 if minute < 3 else 100
        rows.append(f"{timestamp},order-service,{order_disk},20")
        rows.append(f"{timestamp},frontend-gateway,20,20")
    (metric_dir / "metric_service.csv").write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    (log_dir / "log_service.csv").write_text(
        "timestamp,cmdb_id,message\n"
        "2021-03-25 09:04:00,order-service,disk queue warning\n",
        encoding="utf-8",
    )
    (trace_dir / "trace_service.csv").write_text(
        "timestamp,cmdb_id,duration\n"
        "2021-03-25 09:04:00,order-service,500\n",
        encoding="utf-8",
    )
    return tmp_path / "Market"


def test_real_loader_returns_flat_metric_contract(tmp_path):
    data_root = _build_market_fixture(tmp_path)
    config = {
        "system": "Market",
        "dataset": "cloudbed-1",
        "data_root": str(data_root),
        "use_mock": False,
        "default_date": "2021-03-25",
        "top_k": 1,
    }
    query = "Incident on 2021-03-25 from 09:00 to 09:30"

    prediction = run(query, config)

    first = prediction.to_openrca_json()["1"]
    assert first["root cause component"] == "order-service"
    assert first["root cause reason"] == "high disk I/O read usage"


def test_real_loader_reads_logs_and_traces(tmp_path):
    data_root = _build_market_fixture(tmp_path)
    config = {
        "system": "Market",
        "dataset": "cloudbed-1",
        "data_root": str(data_root),
        "use_mock": False,
        "default_date": "2021-03-25",
    }
    window, _ = parse_query("Incident on 2021-03-25 from 09:00 to 09:30")
    telemetry = load(
        config["system"],
        window,
        config["data_root"],
        dataset=config["dataset"],
        include_auxiliary=True,
    )

    assert len(telemetry["metric"]) == 24
    assert len(telemetry["log"]) == 1
    assert len(telemetry["trace"]) == 1


def test_numeric_timestamp_offset_maps_epoch_to_incident_local_time(tmp_path):
    data_root = _build_market_fixture(tmp_path)
    metric_path = (
        data_root
        / "cloudbed-1"
        / "telemetry"
        / "2021_03_25"
        / "metric"
        / "metric_service.csv"
    )
    epoch = int(datetime(2021, 3, 25, 1, 5, tzinfo=timezone.utc).timestamp())
    metric_path.write_text(
        "timestamp,cmdb_id,kpi_name,value\n"
        f"{epoch},order-service,disk_io_read,100\n",
        encoding="utf-8",
    )
    window, _ = parse_query("Incident on 2021-03-25 from 09:00 to 09:30")

    telemetry = load(
        "Market",
        window,
        data_root,
        dataset="cloudbed-1",
        metric_files=["metric_service.csv"],
        timestamp_offset_hours=8,
    )

    assert telemetry["metric"][0]["timestamp"].hour == 9
