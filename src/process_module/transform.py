"""PROCESS module — transform preprocessed telemetry into agent-ready features."""

from __future__ import annotations

import pandas as pd


# =====================================================
# Aggregate Metrics
# =====================================================

def aggregate_metrics(metric_df: pd.DataFrame) -> dict:
    """
    Group metric data by (service, KPI).

    Expected columns:
        - timestamp
        - cmdb_id
        - kpi_name
        - value

    Returns:
        {
            (service, kpi): [value1, value2, ...]
        }
    """

    groups = {}

    if metric_df is None:
        return groups

    if metric_df.empty:
        return groups

    required_columns = {
        "cmdb_id",
        "kpi_name",
        "value",
    }

    if not required_columns.issubset(metric_df.columns):
        return groups

    df = metric_df.copy()

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "cmdb_id",
            "kpi_name",
            "value",
        ]
    )

    # Keep chronological order if timestamp exists
    if "timestamp" in df.columns:
        df = df.sort_values(
            "timestamp"
        )

    for _, row in df.iterrows():

        service = str(
            row["cmdb_id"]
        ).strip()

        kpi = str(
            row["kpi_name"]
        ).strip()

        if not service or not kpi:
            continue

        try:
            value = float(
                row["value"]
            )
        except (
            ValueError,
            TypeError,
        ):
            continue

        groups.setdefault(
            (service, kpi),
            []
        ).append(value)

    return groups


# =====================================================
# Convert Metrics To Features
# =====================================================

def metrics_to_features(metric_df: pd.DataFrame) -> dict:
    """
    Convert metric DataFrame into feature dictionary.

    Returns:

        {
            (service, kpi): {
                "values": [...],
                "n": 10
            }
        }
    """

    groups = aggregate_metrics(
        metric_df
    )

    return {
        key: {
            "values": values,
            "n": len(values),
        }
        for key, values in groups.items()
    }


# =====================================================
# Transform All Telemetry
# =====================================================

def to_features(telemetry) -> dict:
    """
    Transform PreprocessedTelemetry into agent-ready
    metric features.

    Expected:

        telemetry.metrics = {
            dataset_name: DataFrame
        }

    Returns:

        {
            "dataset_name": {
                (service, kpi): {
                    "values": [...],
                    "n": ...
                }
            }
        }
    """

    result = {}

    if telemetry is None:
        return result

    metrics = getattr(
        telemetry,
        "metrics",
        {}
    )

    for dataset_name, df in metrics.items():

        result[dataset_name] = metrics_to_features(
            df
        )

    return result