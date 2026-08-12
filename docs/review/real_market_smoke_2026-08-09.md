# Real Market metric-only smoke reproduction — one read-only case

Purpose: prove that the repaired lightweight loader can read a real multi-gigabyte
Market CSV, apply the incident-time offset/window, and return ranked candidates.
This is one failure case, **not an accuracy estimate and not method tuning**.

## Portable command

Install the review-branch requirements, then point `OPENRCA_MARKET_ROOT` at the
directory that contains `cloudbed-1/`. The command performs no network call or
database write.

```bash
export OPENRCA_MARKET_ROOT=/absolute/path/to/market-parent
python3 - <<'PY'
import json
import os

from src.pipeline import run

query = (
    "The cloud service system, cloudbed-1, experienced one failure within the "
    "time range of March 20, 2022, from 09:00 to 09:30. The specific component "
    "responsible for this failure and the underlying reason are currently "
    "unknown. You are tasked with identifying the root cause component and "
    "the root cause reason."
)
config = {
    "system": "Market",
    "dataset": "cloudbed-1",
    "data_root": os.environ["OPENRCA_MARKET_ROOT"],
    "use_mock": False,
    "default_date": "2022-03-20",
    "timestamp_offset_hours": 8,
    "metric_files": ["metric_container.csv"],
    "include_auxiliary_telemetry": False,
    "top_k": 5,
}
print(json.dumps(run(query, config).to_openrca_json(), indent=2))
PY
```

## Audited input and performance

| Field | Observed value |
|---|---|
| Dataset/task | Market `cloudbed-1`, `task_6` |
| Window | 2022-03-20 09:00–09:30 incident-local time |
| Timestamp offset | UTC telemetry → local time, +8 hours |
| Input file | `telemetry/2022_03_20/metric/metric_container.csv` |
| File bytes | 277,859,576 |
| Elapsed | 13.94 seconds |
| Maximum RSS | 191,564 KB |
| Network/DB/log/trace access | None |

## Exact ranking and truth

Ground truth: `shippingservice-1 / container read I/O load`.

| Rank | Predicted component | Detector reason |
|---:|---|---|
| 1 | `node-6.currencyservice2-0` | `container_memory_rss` |
| 2 | `node-6.adservice-1` | `container_memory_rss` |
| 3 | `node-5.checkoutservice-2` | `container_memory_failures.container.pgfault` |
| 4 | `node-5.shippingservice-2` | `container_fs_reads./dev/vda` |
| 5 | `node-6.frontend2-0` | `container_file_descriptors` |

## Interpretation

This was deliberately a **metric-only lightweight-loader run**, not the
multimodal/full pipeline. Real metric loading/time semantics work, but the
expected service/reason missed top-1
and the related shipping-service replica appeared only at rank 4. An exploratory
score can move a shipping instance to rank 1 while still selecting the wrong KPI,
so this single label is not a valid basis for tuning.

Before changing the detector, define and test replica-name normalization (for
example `shippingservice-1` versus node-qualified or `shippingservice-2` labels),
apply the same rule to truth/prediction/scorer, freeze a multi-case evaluation
manifest, and inspect errors across all 15 failure reasons.
