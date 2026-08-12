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

def normalize_timestamp(df, timestamp_offset_hours=0):

    df = df.copy()

    if "timestamp" not in df.columns:
        return df


    sample = df["timestamp"].dropna()

    if sample.empty:
        return df


    try:
        value = str(int(float(sample.iloc[0])))
    except (TypeError, ValueError):
        value = ""

    unit = {10: "s", 13: "ms"}.get(len(value))


    if unit:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            unit=unit,
            errors="coerce"
        )

        if timestamp_offset_hours:
            df["timestamp"] = df["timestamp"] + pd.Timedelta(
                hours=timestamp_offset_hours
            )

    else:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
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

def preprocess_table(
    file,
    window,
    chunksize=100_000,
    timestamp_offset_hours=0,
):

    print(
        "Processing:",
        file.name
    )


    processed_chunks = []
    columns = []
    for chunk in pd.read_csv(file, chunksize=chunksize):
        if not columns:
            columns = chunk.columns.tolist()
        chunk = normalize_timestamp(
            chunk,
            timestamp_offset_hours=timestamp_offset_hours,
        )
        chunk = filter_time_window(chunk, window)
        chunk = clean_dataframe(chunk)
        if not chunk.empty:
            processed_chunks.append(chunk)

    if processed_chunks:
        df = pd.concat(processed_chunks, ignore_index=True)
        df = clean_dataframe(df)
    else:
        df = pd.DataFrame(columns=columns)


    print(
        "Rows after preprocess:",
        len(df)
    )


    return df

# =====================================================
# Normalize Metric Schema
# =====================================================

def normalize_metric_schema(df):

    # Already normalized format
    if {
        "timestamp",
        "cmdb_id",
        "kpi_name",
        "value"
    }.issubset(df.columns):

        return df


    # metric_service.csv
    if "service" in df.columns:

        rows = []

        kpi_columns = [
            "rr",
            "sr",
            "mrt",
            "count",
        ]


        for _, row in df.iterrows():

            for kpi in kpi_columns:

                if kpi in row:

                    rows.append(
                        {
                            "timestamp": row["timestamp"],
                            "cmdb_id": row["service"],
                            "kpi_name": kpi,
                            "value": row[kpi],
                        }
                    )


        return pd.DataFrame(rows)


    return df


# =====================================================
# STEP 7.6 Process Metrics
# =====================================================

def preprocess_metrics(metadata, window, timestamp_offset_hours=0):

    metrics = {}


    for file in metadata.metric.files:

        df = preprocess_table(
            file,
            window,
            timestamp_offset_hours=timestamp_offset_hours,
        )


        df = normalize_metric_schema(
            df
        )


        if file.stem in metrics:
            metrics[file.stem] = clean_dataframe(
                pd.concat([metrics[file.stem], df], ignore_index=True)
            )
        else:
            metrics[file.stem] = df


    return metrics


# =====================================================
# STEP 7.7 Process Logs
# =====================================================

def preprocess_logs(metadata, window, timestamp_offset_hours=0):

    logs = {}


    for file in metadata.log.files:

        df = preprocess_table(
            file,
            window,
            timestamp_offset_hours=timestamp_offset_hours,
        )

        if file.stem in logs:
            logs[file.stem] = clean_dataframe(
                pd.concat([logs[file.stem], df], ignore_index=True)
            )
        else:
            logs[file.stem] = df


    return logs



# =====================================================
# STEP 7.8 Process Traces
# =====================================================

def preprocess_traces(metadata, window, timestamp_offset_hours=0):

    traces = {}

    for file in metadata.trace.files:

        df = preprocess_table(
            file,
            window,
            timestamp_offset_hours=timestamp_offset_hours,
        )

        if file.stem in traces:
            traces[file.stem] = clean_dataframe(
                pd.concat([traces[file.stem], df], ignore_index=True)
            )
        else:
            traces[file.stem] = df


    return traces



# =====================================================
# STEP 7 MAIN
# =====================================================

def preprocess(
    metadata,
    parsed_query,
    timestamp_offset_hours=0,
):

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
        window,
        timestamp_offset_hours=timestamp_offset_hours,
    )

    logs = preprocess_logs(
        metadata,
        window,
        timestamp_offset_hours=timestamp_offset_hours,
    )

    traces = preprocess_traces(
        metadata,
        window,
        timestamp_offset_hours=timestamp_offset_hours,
    )

    dataset_folder = metadata.metric.folder.parent.parent.parent.name

    return PreprocessedTelemetry(
        dataset=dataset_folder,
        metrics=metrics,
        logs=logs,
        traces=traces,
    )
