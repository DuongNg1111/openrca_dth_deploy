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

from pathlib import Path
import pandas as pd
def load(system: str, window, data_root: str) -> dict:
    """Read REAL OpenRCA telemetry."""

    import pandas as pd
    from pathlib import Path

    # =========================
    # Step 1: Resolve dataset path
    # =========================

    date_folder = window.start.strftime("%Y_%m_%d")

    telemetry_path = (
        Path(data_root)
        / system
        / "telemetry"
        / date_folder
    )

    print("Telemetry path:", telemetry_path)


    # =========================
    # Step 2: Read metric sample
    # =========================

    metric_path = telemetry_path / "metric"

    metric_files = list(metric_path.glob("*.csv"))

    print("\nMetric files:")
    for file in metric_files:
        print("-", file.name)


    # Chỉ đọc 3 dòng đầu mỗi file để kiểm tra
    metric_samples = []

    for file in metric_files:
        print("\nReading:", file.name)

        df = pd.read_csv(
            file,
            nrows=3
        )

        print("Columns:", df.columns.tolist())
        print(df)

        metric_samples.append(df)


    # Gộp sample lại (chỉ vài dòng)
    metric = pd.concat(
        metric_samples,
        ignore_index=True
    )


    return {
        "metric": metric,
        "log": [],
        "trace": []
    }