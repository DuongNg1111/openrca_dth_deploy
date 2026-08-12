from __future__ import annotations

import csv
import math
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

MOCK_COMPONENTS = (
    "frontend-gateway",
    "order-service",
    "shipment-service",
    "tracking-service",
    "warehouse-service",
    "payment-service",
)
MOCK_KPIS = ("cpu", "memory", "disk_io_read", "latency")
ROOT_CAUSE_COMPONENT = "order-service"
SIGNATURE_KPI = "disk_io_read"


def load_mock(window=None, seed: int = 7) -> dict:
    """Return deterministic telemetry with one injected RCA anomaly."""
    random_source = random.Random(seed)
    start = window.start if window else datetime(2021, 3, 25, 9, 0, 0)
    points = 30
    spike_from = points * 2 // 3
    metrics = []

    for step in range(points):
        timestamp = start + timedelta(minutes=step)
        for component in MOCK_COMPONENTS:
            for kpi in MOCK_KPIS:
                value = 20 + 5 * random_source.random()
                if (
                    component == ROOT_CAUSE_COMPONENT
                    and kpi == SIGNATURE_KPI
                    and step >= spike_from
                ):
                    value += 80 + 10 * random_source.random()
                metrics.append(
                    {
                        "timestamp": timestamp,
                        "component": component,
                        "kpi": kpi,
                        "value": round(value, 2),
                    }
                )

    logs = [
        {
            "timestamp": start + timedelta(minutes=spike_from),
            "component": ROOT_CAUSE_COMPONENT,
            "level": "ERROR",
            "message": "injected logistics failure for the mock RCA case",
        }
    ]
    traces = [
        {"timestamp": start, "service": component, "duration_ms": 10}
        for component in MOCK_COMPONENTS
    ]
    return {"metric": metrics, "log": logs, "trace": traces}


def _resolve_telemetry_root(system: str, data_root: str | Path, dataset: str) -> Path:
    root = Path(data_root).expanduser()
    candidates = [
        root,
        root / dataset / "telemetry",
        root / system / dataset / "telemetry",
        root / "telemetry",
    ]
    for candidate in candidates:
        if candidate.name == "telemetry" and candidate.is_dir():
            return candidate

    checked = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Market telemetry directory not found; checked: {checked}")


def _parse_timestamp(value: Any, timestamp_offset_hours: float = 0) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    try:
        numeric = float(text)
    except ValueError:
        numeric = None

    if numeric is not None and math.isfinite(numeric):
        if abs(numeric) >= 1_000_000_000_000:
            numeric /= 1000
        try:
            parsed = datetime.fromtimestamp(numeric, tz=timezone.utc).replace(tzinfo=None)
            return parsed + timedelta(hours=timestamp_offset_hours)
        except (OverflowError, OSError, ValueError):
            return None

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _date_directories(telemetry_root: Path, window) -> list[Path]:
    current_date = window.start.date()
    end_date = window.end.date()
    directories = []
    missing = []
    while current_date <= end_date:
        directory = telemetry_root / current_date.strftime("%Y_%m_%d")
        if directory.is_dir():
            directories.append(directory)
        else:
            missing.append(directory)
        current_date += timedelta(days=1)

    if missing:
        raise FileNotFoundError(
            "Telemetry date coverage is incomplete; missing: "
            + ", ".join(str(path) for path in missing)
        )
    return directories


def _read_modality(
    date_directories: list[Path],
    modality: str,
    window,
    filenames: list[str] | tuple[str, ...] | None = None,
    timestamp_offset_hours: float = 0,
) -> list[dict]:
    records = []
    for date_directory in date_directories:
        modality_directory = date_directory / modality
        csv_paths = (
            sorted(modality_directory.glob("*.csv"))
            if filenames is None
            else [modality_directory / filename for filename in filenames]
        )
        for csv_path in csv_paths:
            if not csv_path.is_file():
                raise FileNotFoundError(csv_path)
            with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                for row in csv.DictReader(csv_file):
                    timestamp = _parse_timestamp(
                        row.get("timestamp"),
                        timestamp_offset_hours=timestamp_offset_hours,
                    )
                    if timestamp is None or not window.contains(timestamp):
                        continue
                    record = dict(row)
                    record["timestamp"] = timestamp
                    records.append(record)
    return records


def _flatten_metrics(rows: list[dict]) -> list[dict]:
    metrics = []
    reserved = {
        "timestamp",
        "component",
        "cmdb_id",
        "service",
        "kpi",
        "kpi_name",
        "value",
    }

    for row in rows:
        component = row.get("component") or row.get("cmdb_id") or row.get("service")
        if not component:
            continue

        kpi = row.get("kpi") or row.get("kpi_name")
        if kpi:
            candidates = [(kpi, row.get("value"))]
        else:
            candidates = [
                (column, value)
                for column, value in row.items()
                if column not in reserved
            ]

        for metric_name, raw_value in candidates:
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(value):
                continue
            metrics.append(
                {
                    "timestamp": row["timestamp"],
                    "component": str(component),
                    "kpi": str(metric_name),
                    "value": value,
                }
            )

    return metrics


def load(
    system: str,
    window,
    data_root: str | Path,
    dataset: str = "cloudbed-1",
    metric_files: list[str] | tuple[str, ...] | None = None,
    include_auxiliary: bool = False,
    timestamp_offset_hours: float = 0,
) -> dict:
    """Load a local Market-compatible telemetry slice without external writes.

    Supported metric schemas are the normalized
    ``timestamp,cmdb_id,kpi_name,value`` layout and wide service metrics such
    as ``timestamp,service,rr,sr,mrt,count``. Returned metric records use the
    flat contract consumed by ``detect.rank_components``. Logs and traces are
    opt-in because the lightweight detector does not consume them and Market
    auxiliary files can be several gigabytes each.
    """
    if window.end <= window.start:
        raise ValueError("Telemetry window end must be after start")

    telemetry_root = _resolve_telemetry_root(system, data_root, dataset)
    date_directories = _date_directories(telemetry_root, window)
    metric_rows = _read_modality(
        date_directories,
        "metric",
        window,
        filenames=metric_files,
        timestamp_offset_hours=timestamp_offset_hours,
    )
    metrics = _flatten_metrics(metric_rows)
    if not metrics:
        raise ValueError("No usable metric records were found in the requested window")

    logs = (
        _read_modality(
            date_directories,
            "log",
            window,
            timestamp_offset_hours=timestamp_offset_hours,
        )
        if include_auxiliary
        else []
    )
    traces = (
        _read_modality(
            date_directories,
            "trace",
            window,
            timestamp_offset_hours=timestamp_offset_hours,
        )
        if include_auxiliary
        else []
    )
    return {"metric": metrics, "log": logs, "trace": traces}


def connect_data_source(parsed_query, config):
    """
    Step 5
    5.1 Connect Raw Database
    5.2 Verify Connection
    5.3 Select Data Source
    """

    system = config["system"]
    data_root = config["data_root"]

    # =========================
    # Step 5.1 Connect Raw Database
    # =========================

    environment_map = {
        "Cloud A": "cloudbed-1",
        "Cloud B": "cloudbed-2",
    }

    dataset_override = config.get("dataset_override")
    if dataset_override is not None:
        if not isinstance(dataset_override, str):
            raise TypeError("Dataset override must be a string folder name")

        dataset_folder = dataset_override.strip()
        if (
            dataset_folder != dataset_override
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", dataset_folder)
            or dataset_folder.endswith(".")
        ):
            raise ValueError(
                "Dataset override must be a single safe folder name "
                "containing only letters, numbers, '.', '_' or '-'"
            )
    else:
        dataset_folder = environment_map.get(parsed_query.environment)

        if dataset_folder is None:
            raise ValueError(
                f"Unknown environment: {parsed_query.environment}"
            )

    # Ưu tiên data_root trong config
    base_path = Path(data_root)
    dataset_path = base_path / dataset_folder / "telemetry"

    # =========================
    # Step 5.2 Verify Connection
    # =========================

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    # =========================
    # Step 5.3 Select Data Source
    # =========================

    print("=" * 40)
    print("DATA SOURCE")
    print("=" * 40)
    print("System      :", system)
    print("Environment :", parsed_query.environment)
    print("Dataset     :", dataset_folder)
    print("Dataset Path:", dataset_path)

    return dataset_path
