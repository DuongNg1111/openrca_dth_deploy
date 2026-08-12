from datetime import date, datetime, timedelta
from pathlib import Path

from src.schemas import MetadataIndex, TelemetryMetadata


def _as_datetime(incident_time) -> datetime:
    if isinstance(incident_time, str):
        # Convert Jira timezone +0700 -> +07:00 for ``fromisoformat``.
        if (
            len(incident_time) >= 5
            and incident_time[-5] in ["+", "-"]
            and incident_time[-4:].isdigit()
        ):
            incident_time = incident_time[:-2] + ":" + incident_time[-2:]
        return datetime.fromisoformat(incident_time)

    if isinstance(incident_time, datetime):
        return incident_time

    raise TypeError(f"Unsupported incident_time type: {type(incident_time)}")


def _covered_dates(parsed_query) -> list[date]:
    """Return every calendar date touched by the inclusive query window."""
    window = getattr(parsed_query, "time_window", None)
    if window is None:
        return [_as_datetime(parsed_query.incident_time).date()]

    if not isinstance(window.start, datetime) or not isinstance(window.end, datetime):
        raise TypeError("parsed_query.time_window start and end must be datetimes")
    if window.end < window.start:
        raise ValueError("parsed_query.time_window end must not be before start")

    current = window.start.date()
    end = window.end.date()
    dates = []
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def _get_date_folders(dataset_path: Path, parsed_query) -> list[Path]:
    dataset_path = Path(dataset_path)
    folders = [
        dataset_path / covered_date.strftime("%Y_%m_%d")
        for covered_date in _covered_dates(parsed_query)
    ]
    missing = [folder for folder in folders if not folder.is_dir()]
    if missing:
        raise FileNotFoundError(
            "Telemetry date coverage is incomplete; missing date folders: "
            + ", ".join(str(folder) for folder in missing)
        )
    return folders


def _get_date_folder(dataset_path: Path, incident_time) -> Path:
    """Compatibility helper for callers that request one incident date."""
    folder = Path(dataset_path) / _as_datetime(incident_time).strftime("%Y_%m_%d")
    if not folder.is_dir():
        raise FileNotFoundError(folder)
    return folder


def _load_modality_metadata(
    date_folders: list[Path],
    modality: str,
) -> TelemetryMetadata:
    modality_folders = [date_folder / modality for date_folder in date_folders]
    missing = [folder for folder in modality_folders if not folder.is_dir()]
    if missing:
        raise FileNotFoundError(
            f"Telemetry {modality} coverage is incomplete; missing folders: "
            + ", ".join(str(folder) for folder in missing)
        )

    files = [
        file
        for folder in modality_folders
        for file in sorted(folder.glob("*.csv"))
    ]
    return TelemetryMetadata(
        # This remains a representative folder for compatibility. ``files``
        # contains the complete ordered multi-date set.
        folder=modality_folders[0],
        files=files,
        count=len(files),
    )


# ======================================================
# STEP 6.1
# ======================================================

def load_metric_metadata(dataset_path, parsed_query):
    return _load_modality_metadata(
        _get_date_folders(dataset_path, parsed_query),
        "metric",
    )


# ======================================================
# STEP 6.2
# ======================================================

def load_log_metadata(dataset_path, parsed_query):
    return _load_modality_metadata(
        _get_date_folders(dataset_path, parsed_query),
        "log",
    )


# ======================================================
# STEP 6.3
# ======================================================

def load_trace_metadata(dataset_path, parsed_query):
    return _load_modality_metadata(
        _get_date_folders(dataset_path, parsed_query),
        "trace",
    )


# ======================================================
# STEP 6.4
# ======================================================

def build_metadata_index(dataset_path, parsed_query):
    date_folders = _get_date_folders(dataset_path, parsed_query)
    metric = _load_modality_metadata(date_folders, "metric")
    log = _load_modality_metadata(date_folders, "log")
    trace = _load_modality_metadata(date_folders, "trace")

    return MetadataIndex(
        date=",".join(folder.name for folder in date_folders),
        metric=metric,
        log=log,
        trace=trace,
        total_files=metric.count + log.count + trace.count,
    )


# ======================================================
# Compatibility API for legacy pipeline/tests
# ======================================================

def load_metadata(dataset_path, parsed_query):
    return build_metadata_index(
        dataset_path,
        parsed_query,
    )
