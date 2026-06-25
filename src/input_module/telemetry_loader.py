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


def load_mock(window=None, seed: int = 7) -> dict:
    """Deterministic mock telemetry with ONE injected anomaly (change-point in the last third).

    Returns: {"metric": [ {timestamp, component, kpi, value}, ... ], "log": [...], "trace": [...] }.
    """
    rng = random.Random(seed)
    start = window.start if window else datetime(2021, 3, 25, 9, 0, 0)
    points = 30
    spike_from = points * 2 // 3
    metric = []
    for step in range(points):
        ts = start + timedelta(minutes=step)
        for comp in MOCK_COMPONENTS:
            for kpi in MOCK_KPIS:
                value = 20 + 5 * rng.random()  # quiet baseline
                if comp == ROOT_CAUSE_COMPONENT and kpi == SIGNATURE_KPI and step >= spike_from:
                    value += 80 + 10 * rng.random()  # injected failure
                metric.append(
                    {"timestamp": ts, "component": comp, "kpi": kpi, "value": round(value, 2)}
                )
    log = [
        {"timestamp": start + timedelta(minutes=spike_from), "component": ROOT_CAUSE_COMPONENT,
         "level": "ERROR", "message": "demo error for logistics root cause"}
    ]
    trace = [{"timestamp": start, "service": c, "duration_ms": 10} for c in MOCK_COMPONENTS]
    return {"metric": metric, "log": log, "trace": trace}


def load(system: str, window, data_root: str) -> dict:
    """TODO(DEV 1): read REAL OpenRCA telemetry for `system` within `window`.

    Steps:
      1. Resolve dataset/{system}/telemetry/{date}.
      2. Read metric/, log/, trace/ (CSV/JSON) with pandas.
      3. Filter rows to [window.start, window.end].
      4. Return the same dict shape as load_mock().
    """
    raise NotImplementedError(
        "DEV 1: implement real telemetry loading — see docs/05_pipeline_and_modules.md"
    )
