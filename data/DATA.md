# Dataset — Market

The `data/` folder is **gitignored** (telemetry is ~tens of GB). Download it locally.

## 1. Download
OpenRCA telemetry (Google Drive link in the upstream README):
https://github.com/microsoft/OpenRCA  →  the Drive folder under *Dataset*.

## 2. Expected layout (after download)
```
data/
└── Market/cloudbed-1/
    ├── query.csv        # the failure queries (input)
    ├── record.csv       # ground-truth root causes
    └── telemetry/
        └── {YYYY_MM_DD}/
            ├── metric    # KPI time series
            ├── log       # semi-structured logs
            └── trace     # call/dependency traces
```
> Note: OpenRCA timestamps are **UTC+8**. Full benchmark needs ~80 GB disk / 32 GB RAM.

## 3. Quick check
```bash
python -c "import os; print(sorted(os.listdir('data/Market/cloudbed-1')))"
```

## 4. Don't have it yet?
You don't need it to start — the pipeline runs on **mock** telemetry (`use_mock: true`).
Switch to real data in M3/M4 by setting `use_mock: false` and implementing the loaders.
