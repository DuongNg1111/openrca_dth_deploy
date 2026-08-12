from datetime import date, datetime, timedelta
from pathlib import Path

from src.schemas import MetadataIndex, TelemetryMetadata


# ======================================================
# DATETIME HELPERS
# ======================================================

def _as_datetime(incident_time) -> datetime:
    """
    Convert incident_time into a datetime object.

    Supports:
        - datetime
        - ISO string
        - Jira timezone format such as +0700
    """

    if isinstance(incident_time, str):

        # Convert Jira timezone:
        # +0700 -> +07:00
        if (
            len(incident_time) >= 5
            and incident_time[-5] in ["+", "-"]
            and incident_time[-4:].isdigit()
        ):
            incident_time = (
                incident_time[:-2]
                + ":"
                + incident_time[-2:]
            )

        return datetime.fromisoformat(
            incident_time
        )

    if isinstance(incident_time, datetime):
        return incident_time

    raise TypeError(
        f"Unsupported incident_time type: "
        f"{type(incident_time)}"
    )


# ======================================================
# COVERED DATES
# ======================================================

def _covered_dates(parsed_query) -> list[date]:
    """
    Return every calendar date touched
    by the inclusive investigation window.
    """

    window = getattr(
        parsed_query,
        "time_window",
        None,
    )

    # No investigation window
    if window is None:

        return [
            _as_datetime(
                parsed_query.incident_time
            ).date()
        ]

    if not isinstance(
        window.start,
        datetime,
    ):

        raise TypeError(
            "parsed_query.time_window "
            "start must be a datetime"
        )

    if not isinstance(
        window.end,
        datetime,
    ):

        raise TypeError(
            "parsed_query.time_window "
            "end must be a datetime"
        )

    if window.end < window.start:

        raise ValueError(
            "parsed_query.time_window end "
            "must not be before start"
        )

    current = window.start.date()

    end = window.end.date()

    dates = []

    while current <= end:

        dates.append(
            current
        )

        current += timedelta(
            days=1
        )

    return dates


# ======================================================
# GET DATE FOLDERS
# ======================================================

def _get_date_folders(
    dataset_path: Path,
    parsed_query,
) -> list[Path]:

    """
    Return telemetry date folders that actually exist.

    Missing date folders are NOT treated as a pipeline error.

    They simply mean that there may be no telemetry data
    available for the requested investigation window.

    The pipeline will later determine this through
    _has_telemetry_data().
    """

    dataset_path = Path(
        dataset_path
    )

    folders = [
        dataset_path
        / covered_date.strftime(
            "%Y_%m_%d"
        )
        for covered_date in _covered_dates(
            parsed_query
        )
    ]

    existing_folders = [
        folder
        for folder in folders
        if folder.is_dir()
    ]

    return existing_folders


# ======================================================
# COMPATIBILITY HELPER
# ======================================================

def _get_date_folder(
    dataset_path: Path,
    incident_time,
) -> Path:

    """
    Compatibility helper for callers
    that request one incident date.
    """

    folder = (
        Path(dataset_path)
        / _as_datetime(
            incident_time
        ).strftime("%Y_%m_%d")
    )

    if not folder.is_dir():

        raise FileNotFoundError(
            folder
        )

    return folder


# ======================================================
# LOAD MODALITY METADATA
# ======================================================

def _load_modality_metadata(
    date_folders: list[Path],
    modality: str,
) -> TelemetryMetadata:

    """
    Load telemetry files for one modality.

    Supported modalities:

        metric
        log
        trace

    If there are no available date folders,
    return empty metadata instead of raising an error.
    """

    # --------------------------------------------------
    # NO DATE FOLDER
    # --------------------------------------------------

    if not date_folders:

        return TelemetryMetadata(
            folder=Path(""),
            files=[],
            count=0,
        )

    # --------------------------------------------------
    # FIND EXISTING MODALITY FOLDERS
    # --------------------------------------------------

    modality_folders = [
        date_folder / modality
        for date_folder in date_folders
        if (
            date_folder / modality
        ).is_dir()
    ]

    # --------------------------------------------------
    # NO MODALITY FOLDER
    # --------------------------------------------------

    if not modality_folders:

        return TelemetryMetadata(
            folder=Path(""),
            files=[],
            count=0,
        )

    # --------------------------------------------------
    # LOAD CSV FILES
    # --------------------------------------------------

    files = [
        file
        for folder in modality_folders
        for file in sorted(
            folder.glob("*.csv")
        )
    ]

    # --------------------------------------------------
    # RETURN METADATA
    # --------------------------------------------------

    return TelemetryMetadata(
        # Representative folder
        # for compatibility.
        folder=modality_folders[0],

        files=files,

        count=len(files),
    )


# ======================================================
# STEP 6.1
# LOAD METRIC METADATA
# ======================================================

def load_metric_metadata(
    dataset_path,
    parsed_query,
):

    date_folders = _get_date_folders(
        dataset_path,
        parsed_query,
    )

    return _load_modality_metadata(
        date_folders,
        "metric",
    )


# ======================================================
# STEP 6.2
# LOAD LOG METADATA
# ======================================================

def load_log_metadata(
    dataset_path,
    parsed_query,
):

    date_folders = _get_date_folders(
        dataset_path,
        parsed_query,
    )

    return _load_modality_metadata(
        date_folders,
        "log",
    )


# ======================================================
# STEP 6.3
# LOAD TRACE METADATA
# ======================================================

def load_trace_metadata(
    dataset_path,
    parsed_query,
):

    date_folders = _get_date_folders(
        dataset_path,
        parsed_query,
    )

    return _load_modality_metadata(
        date_folders,
        "trace",
    )


# ======================================================
# STEP 6.4
# BUILD METADATA INDEX
# ======================================================

def build_metadata_index(
    dataset_path,
    parsed_query,
):

    date_folders = _get_date_folders(
        dataset_path,
        parsed_query,
    )

    # --------------------------------------------------
    # LOAD EACH TELEMETRY MODALITY
    # --------------------------------------------------

    metric = _load_modality_metadata(
        date_folders,
        "metric",
    )

    log = _load_modality_metadata(
        date_folders,
        "log",
    )

    trace = _load_modality_metadata(
        date_folders,
        "trace",
    )

    # --------------------------------------------------
    # DATE INFORMATION
    # --------------------------------------------------

    date_value = ",".join(
        folder.name
        for folder in date_folders
    )

    if not date_value:

        date_value = "No telemetry date available"

    # --------------------------------------------------
    # RETURN METADATA INDEX
    # --------------------------------------------------

    return MetadataIndex(
        date=date_value,

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
# COMPATIBILITY API
# ======================================================

def load_metadata(
    dataset_path,
    parsed_query,
):

    return build_metadata_index(
        dataset_path,
        parsed_query,
    )