import pandas as pd

from src.schemas import PreprocessedTelemetry


# =====================================================
# STEP 7.1 Build Investigation Window
# =====================================================

def build_investigation_window(parsed_query):
    """
    Create 30 minutes investigation window.

    Example:
        Incident:
        09:30

        Window:
        09:15 - 09:45
    """

    incident_time = parsed_query.incident_time

    start = incident_time - pd.Timedelta(minutes=15)

    end = incident_time + pd.Timedelta(minutes=15)

    return {
        "start": start,
        "end": end
    }



# =====================================================
# STEP 7.2 Normalize Timestamp
# =====================================================

def normalize_timestamp(df):

    df = df.copy()

    if "timestamp" not in df.columns:
        return df


    sample = df["timestamp"].dropna()

    if sample.empty:
        return df


    value = str(int(sample.iloc[0]))


    if len(value) == 10:
        unit = "s"

    elif len(value) == 13:
        unit = "ms"

    else:
        unit = None


    if unit:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            unit=unit,
            errors="coerce"
        )


    return df



# =====================================================
# STEP 7.3 Filter Investigation Window
# =====================================================

def filter_time_window(df, window):

    if "timestamp" not in df.columns:
        return df


    df = df[
        (df["timestamp"] >= window["start"])
        &
        (df["timestamp"] <= window["end"])
    ]


    return df



# =====================================================
# STEP 7.4 Remove Invalid Records
# =====================================================

def clean_dataframe(df):

    df = df.copy()


    # Remove completely empty rows

    df = df.dropna(
        how="all"
    )


    # Remove duplicates

    df = df.drop_duplicates()


    # Trace duration cannot be negative

    if "duration" in df.columns:

        df = df[
            (df["duration"].isna())
            |
            (df["duration"] >= 0)
        ]


    return df.reset_index(drop=True)



# =====================================================
# STEP 7.5 Process One Table
# =====================================================

def preprocess_table(file, window):

    print(
        "Processing:",
        file.name
    )


    df = pd.read_csv(file)


    df = normalize_timestamp(df)


    df = filter_time_window(
        df,
        window
    )


    df = clean_dataframe(df)


    print(
        "Rows after preprocess:",
        len(df)
    )


    return df



# =====================================================
# STEP 7.6 Process Metrics
# =====================================================

def preprocess_metrics(metadata, window):

    metrics = {}


    for file in metadata.metric.files:

        metrics[file.stem] = preprocess_table(
            file,
            window
        )


    return metrics



# =====================================================
# STEP 7.7 Process Logs
# =====================================================

def preprocess_logs(metadata, window):

    logs = {}


    for file in metadata.log.files:

        logs[file.stem] = preprocess_table(
            file,
            window
        )


    return logs



# =====================================================
# STEP 7.8 Process Traces
# =====================================================

def preprocess_traces(metadata, window):

    traces = {}


    for file in metadata.trace.files:

        traces[file.stem] = preprocess_table(
            file,
            window
        )


    return traces



# =====================================================
# STEP 7 MAIN
# =====================================================

def preprocess(
    metadata,
    parsed_query,
):

    print("\n==============================")
    print(" STEP 7: PREPROCESS TELEMETRY ")
    print("==============================")


    window = build_investigation_window(
        parsed_query
    )


    print("\nIncident Time:")
    print(parsed_query.incident_time)


    print("\nInvestigation Window:")
    print(
        window["start"],
        "->",
        window["end"]
    )


    metrics = preprocess_metrics(
        metadata,
        window
    )


    logs = preprocess_logs(
        metadata,
        window
    )


    traces = preprocess_traces(
        metadata,
        window
    )

    print("DEBUG METRIC FOLDER:", metadata.metric.folder)
    dataset_folder = metadata.metric.folder.parent.parent.parent.name

    return PreprocessedTelemetry(
        dataset=dataset_folder,
        metrics=metrics,
        logs=logs,
        traces=traces
    )
print("\n==============================")
print(" STEP 7 COMPLETED ")
print("==============================")

