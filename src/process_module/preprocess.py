import pandas as pd

from src.schemas import PreprocessedTelemetry


# =====================================================
# STEP 7.1 Handle Missing Values
# =====================================================

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows where all values are missing.
    """
    return df.dropna(how="all")


# =====================================================
# STEP 7.2 Normalize Timestamp
# =====================================================

def normalize_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize timestamp columns to pandas datetime.

    Rules
    -----
    - 10 digits -> Unix seconds
    - 13 digits -> Unix milliseconds
    """

    df = df.copy()

    timestamp_candidates = [
        "timestamp",
        "time",
        "datetime",
        "start_time",
        "end_time",
    ]

    for col in timestamp_candidates:

        if col not in df.columns:
            continue

        # lấy giá trị đầu tiên không NULL
        sample = df[col].dropna()

        if sample.empty:
            continue

        try:
            sample = str(int(float(sample.iloc[0])))
        except (ValueError, TypeError):
            continue

        if len(sample) == 10:
            unit = "s"

        elif len(sample) == 13:
            unit = "ms"

        else:
            # nếu timestamp không đúng chuẩn --> convert và báo NaT
            unit = "s"

        df[col] = pd.to_datetime(
            df[col],
            unit=unit,
            errors="coerce",
        )

    return df

# =====================================================
# STEP 7.3 Normalize Data Types
# =====================================================

def normalize_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize dataframe dtypes.

    Currently pandas infers most dtypes automatically when
    reading CSV files. Timestamp columns have already been
    normalized in Step 7.2, therefore no additional processing
    is required here.
    """

    return df


# =====================================================
# STEP 7.4 Remove Invalid Records
# =====================================================

def remove_invalid_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove invalid records from telemetry dataframe.

    Rules
    -----
    1. Remove duplicate rows.
    2. Remove records with negative duration.
    3. Keep rows with missing timestamps.
       They will naturally be excluded when building the
       investigation time window in Step 9.
    """

    df = df.copy()

    # -------------------------------------------------
    # Remove duplicate rows
    # -------------------------------------------------
    df = df.drop_duplicates()

    # -------------------------------------------------
    # Remove negative duration (Trace only)
    # -------------------------------------------------
    if "duration" in df.columns:

        df = df[
            (df["duration"].isna()) |
            (df["duration"] >= 0)
        ]

    return df.reset_index(drop=True)

# =====================================================
# STEP 7.5: Build PreprocessedTelemetry
# =====================================================

def preprocess(metadata):
    """
    STEP 7
    Data Preprocessing

    Returns
    -------
    PreprocessedTelemetry
        Cleaned metrics, logs and traces.
    """

    print("\nStarting preprocessing...\n")

    metrics = preprocess_metrics(metadata)

    logs = preprocess_logs(metadata)

    traces = preprocess_traces(metadata)

    print("\nPreprocessing completed.\n")

    return PreprocessedTelemetry(
        metrics=metrics,
        logs=logs,
        traces=traces,
    )