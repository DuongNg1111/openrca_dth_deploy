from datetime import datetime
from pathlib import Path

from src.schemas import (
    TelemetryMetadata,
    MetadataIndex,
)


def _get_date_folder(dataset_path: Path, incident_time: str) -> Path:
    """
    Convert:

        2022-03-20T20:30:00.000+0700

    to:

        telemetry/2022_03_20
    """

    # Convert Jira timezone format +0700 -> +07:00
    if incident_time[-5] in ["+", "-"] and incident_time[-4:].isdigit():
        incident_time = (
            incident_time[:-2]
            + ":"
            + incident_time[-2:]
        )

    dt = datetime.fromisoformat(incident_time)

    folder = dataset_path / dt.strftime("%Y_%m_%d")

    if not folder.exists():
        raise FileNotFoundError(folder)

    return folder

# ======================================================
# STEP 6.1
# ======================================================

def load_metric_metadata(dataset_path, parsed_query):

    date_folder = _get_date_folder(
        dataset_path,
        parsed_query.incident_time,
    )

    folder = date_folder / "metric"

    files = sorted(folder.glob("*.csv"))

    return TelemetryMetadata(
        folder=folder,
        files=files,
        count=len(files),
    )


# ======================================================
# STEP 6.2
# ======================================================

def load_log_metadata(dataset_path, parsed_query):

    date_folder = _get_date_folder(
        dataset_path,
        parsed_query.incident_time,
    )

    folder = date_folder / "log"

    files = sorted(folder.glob("*.csv"))

    return TelemetryMetadata(
        folder=folder,
        files=files,
        count=len(files),
    )


# ======================================================
# STEP 6.3
# ======================================================

def load_trace_metadata(dataset_path, parsed_query):

    date_folder = _get_date_folder(
        dataset_path,
        parsed_query.incident_time,
    )

    folder = date_folder / "trace"

    files = sorted(folder.glob("*.csv"))

    return TelemetryMetadata(
        folder=folder,
        files=files,
        count=len(files),
    )


# ======================================================
# STEP 6.4
# ======================================================

def build_metadata_index(dataset_path, parsed_query):

    metric = load_metric_metadata(
        dataset_path,
        parsed_query,
    )

    log = load_log_metadata(
        dataset_path,
        parsed_query,
    )

    trace = load_trace_metadata(
        dataset_path,
        parsed_query,
    )

    return MetadataIndex(
        date=_get_date_folder(
            dataset_path,
            parsed_query.incident_time,
        ).name,

        metric=metric,

        log=log,

        trace=trace,

        total_files=(
            metric.count
            + log.count
            + trace.count
        ),
    )

# ======================================================
#  Compatibility API for legacy pipeline/tests
# ======================================================
def load_metadata(dataset_path, parsed_query):
    return build_metadata_index(
        dataset_path,
        parsed_query,
    )