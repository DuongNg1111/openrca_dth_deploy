"""INPUT module — load telemetry (metric / log / trace).

For now this provides MOCK data so the whole pipeline runs out of the box.
TODO(DEV 1): implement real loaders for dataset/Market/telemetry/{date}/.
"""
from __future__ import annotations


import random
from datetime import datetime, timedelta

MOCK_COMPONENTS = ['frontend-gateway', 'order-service', 'shipment-service', 'tracking-service', 'warehouse-service', 'payment-service']
MOCK_KPIS = ['cpu', 'memory', 'disk_io_read', 'latency']
SIGNATURE_KPI = "disk_io_read"
ROOT_CAUSE_COMPONENT = "order-service"

#TEST DATA
# from pathlib import Path
# import pandas as pd
# def load(system: str, window, data_root: str) -> dict:
#     """
#     Read REAL OpenRCA telemetry.
#     (Current version: Explore dataset only)
#     """

#     # =====================================================
#     # Step 1: Resolve dataset path
#     # =====================================================
#     date_folder = window.start.strftime("%Y_%m_%d")

#     telemetry_path = (
#         Path(data_root)
#         / system
#         / "telemetry"
#         / date_folder
#     )

#     if not telemetry_path.exists():
#         raise FileNotFoundError(
#             f"Telemetry folder not found: {telemetry_path}"
#         )

#     print("=" * 60)
#     print("Telemetry path:", telemetry_path)
#     print("=" * 60)

#     # =====================================================
#     # Step 2: Read Metric (header + 5 rows)
#     # =====================================================
#     metric = pd.DataFrame()

#     metric_path = telemetry_path / "metric"

#     if metric_path.exists():

#         metric_files = sorted(metric_path.glob("*.csv"))

#         print(f"\nFound {len(metric_files)} metric files")

#         for file in metric_files:

#             print(f"\nReading metric: {file.name}")

#             df = pd.read_csv(file, nrows=5)

#             print("Columns:")
#             print(df.columns.tolist())

#             print(df)

#             metric = df

#     else:
#         print("Metric folder not found.")

#     # =====================================================
#     # Step 3: Read Log (header + 5 rows)
#     # =====================================================
#     log = pd.DataFrame()

#     log_path = telemetry_path / "log"

#     if log_path.exists():

#         log_files = sorted(log_path.glob("*.csv"))

#         print(f"\nFound {len(log_files)} log files")

#         for file in log_files:

#             print(f"\nReading log: {file.name}")

#             df = pd.read_csv(file, nrows=5)

#             print("Columns:")
#             print(df.columns.tolist())

#             print(df)

#             log = df

#     else:
#         print("Log folder not found.")

#     # =====================================================
#     # Step 4: Read Trace (header + 5 rows)
#     # =====================================================
#     trace = pd.DataFrame()

#     trace_path = telemetry_path / "trace"

#     if trace_path.exists():

#         trace_files = sorted(trace_path.glob("*.csv"))

#         print(f"\nFound {len(trace_files)} trace files")

#         for file in trace_files:

#             print(f"\nReading trace: {file.name}")

#             df = pd.read_csv(file, nrows=5)

#             print("Columns:")
#             print(df.columns.tolist())

#             print(df)

#             trace = df

#     else:
#         print("Trace folder not found.")

#     # =====================================================
#     # Summary
#     # =====================================================
#     print("\n========== SUMMARY ==========")
#     print(f"Metric sample rows : {len(metric)}")
#     print(f"Log sample rows    : {len(log)}")
#     print(f"Trace sample rows  : {len(trace)}")

#     return {
#         "metric": metric,
#         "log": log,
#         "trace": trace,
#     }

#IMPLEMENT DATA
from pathlib import Path
import pandas as pd


def load(system: str, window, data_root: str) -> dict:
    """
    Load real OpenRCA telemetry.

    Return:
    {
        "metric": dataframe,
        "log": dataframe,
        "trace": dataframe
    }
    """

    # =====================================================
    # Step 1: Resolve dataset path
    # =====================================================

    date_folder = window.start.strftime("%Y_%m_%d")

    telemetry_path = (
        Path(data_root)
        / system
        / "telemetry"
        / date_folder
    )

    if not telemetry_path.exists():
        raise FileNotFoundError(
            f"Telemetry folder not found: {telemetry_path}"
        )

    print("Telemetry path:", telemetry_path)


    # =====================================================
    # Step 2: Load Metric
    # =====================================================

    metric_frames = []

    metric_path = telemetry_path / "metric"

    metric_files = sorted(metric_path.glob("*.csv"))

    print("\nMetric files:", len(metric_files))


    for file in metric_files:

        print("Reading metric:", file.name)

        for chunk in pd.read_csv(
            file,
            chunksize=10000
        ):

            # convert timestamp
            chunk["timestamp"] = pd.to_datetime(
                chunk["timestamp"],
                unit="s"
            )


            # filter investigation window
            chunk = chunk[
                (chunk["timestamp"] >= window.start)
                &
                (chunk["timestamp"] <= window.end)
            ]


            if not chunk.empty:
                metric_frames.append(chunk)



    if metric_frames:
        metric = pd.concat(
            metric_frames,
            ignore_index=True
        )
    else:
        metric = pd.DataFrame()



    print(
        "Metric rows after filter:",
        len(metric)
    )


    # =====================================================
    # Step 3: Load Log
    # =====================================================

    log_frames = []

    log_path = telemetry_path / "log"

    log_files = sorted(log_path.glob("*.csv"))

    print("\nLog files:", len(log_files))


    for file in log_files:

        print("Reading log:", file.name)

        for chunk in pd.read_csv(
            file,
            chunksize=10000
        ):

            if "timestamp" in chunk.columns:

                chunk["timestamp"] = pd.to_datetime(
                    chunk["timestamp"],
                    unit="s"
                )


                chunk = chunk[
                    (chunk["timestamp"] >= window.start)
                    &
                    (chunk["timestamp"] <= window.end)
                ]


            if not chunk.empty:
                log_frames.append(chunk)



    if log_frames:
        log = pd.concat(
            log_frames,
            ignore_index=True
        )
    else:
        log = pd.DataFrame()


    print(
        "Log rows after filter:",
        len(log)
    )



    # =====================================================
    # Step 4: Load Trace
    # =====================================================

    trace_frames = []

    trace_path = telemetry_path / "trace"

    trace_files = sorted(trace_path.glob("*.csv"))

    print("\nTrace files:", len(trace_files))


    for file in trace_files:

        print("Reading trace:", file.name)

        for chunk in pd.read_csv(
            file,
            chunksize=10000
        ):

            if "timestamp" in chunk.columns:

                # trace timestamp đang là milliseconds
                chunk["timestamp"] = pd.to_datetime(
                    chunk["timestamp"],
                    unit="ms"
                )


                chunk = chunk[
                    (chunk["timestamp"] >= window.start)
                    &
                    (chunk["timestamp"] <= window.end)
                ]


            if not chunk.empty:
                trace_frames.append(chunk)



    if trace_frames:
        trace = pd.concat(
            trace_frames,
            ignore_index=True
        )
    else:
        trace = pd.DataFrame()



    print(
        "Trace rows after filter:",
        len(trace)
    )


    # =====================================================
    # Return contract
    # =====================================================

    return {
    "metric": metric.to_dict("records"),
    "log": log.to_dict("records"),
    "trace": trace.to_dict("records"),
}