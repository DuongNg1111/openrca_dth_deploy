# Market cloudbed-1 dataset card — verified server copy

Evidence date: 2026-08-09, Asia/Ho_Chi_Minh. The dataset was copied from the DTH
student EC2 host through SSH into a local credential-protected runtime directory.
Raw data is not committed to Git.

## Provenance and integrity

| Field | Verified value |
|---|---|
| Source | Microsoft OpenRCA Market `cloudbed-1` corpus on the student server |
| Server source | `/home/ubuntu/Market/cloudbed-1` |
| Local audit copy | `runtime/dth/cloudbed-1` outside this Git repository |
| Logical bytes | 11,936,971,181 (about 12 GB) |
| `query.csv` SHA-256 | `3512ba2d72648f251e7e01733f079c492a4ff573de557a0223ea538bd9c06742` |
| `record.csv` SHA-256 | `6246b65915ecaa948037875a149a3d50afdc730371c8b4e3785799995d589324` |
| Per-file manifest | `market_cloudbed1_file_manifest_2026-08-09.tsv` (20 files; SHA-256 `2e4758131deba52e2ad2a2ae26b72055931f23ec23023d3ef0f321948891eb00`) |
| Raw-data policy | Keep immutable and ignored; do not commit or send through Slack |

Primary project: <https://github.com/microsoft/OpenRCA>
Primary paper: <https://openreview.net/forum?id=M4qNIzQYpd>

The students must confirm applicable terms from the primary source before any
redistribution.

## Coverage

| Item | Verified value |
|---|---:|
| Logical query rows | 70 |
| Ground-truth record rows | 70 |
| Ground-truth components | 29 |
| Ground-truth reasons | 15 |
| Telemetry dates | 2 (`2022_03_20`, `2022_03_21`) |
| Metric files | 10 |
| Log files | 4 |
| Trace files | 2 |
| Metric data lines (headers excluded) | 15,455,234 |
| Log data lines (headers excluded) | 25,772,490 |
| Trace data lines (headers excluded) | 18,160,322 |
| CSV files including query/record | 18 |
| Total files | 20 (includes 2 `.DS_Store` metadata files) |

## Ground-truth distribution

| Reason | Records |
|---|---:|
| container read I/O load | 8 |
| container memory load | 7 |
| container CPU load | 7 |
| container network packet corruption | 6 |
| node memory consumption | 5 |
| node disk read I/O consumption | 5 |
| node disk write I/O consumption | 5 |
| container network packet retransmission | 5 |
| node disk space consumption | 5 |
| node CPU load | 4 |
| container network latency | 4 |
| container process termination | 4 |
| node CPU spike | 2 |
| container packet loss | 2 |
| container write I/O load | 1 |

There are 29 component labels. The largest groups are node-4 (7), node-1 (5),
node-6 (5), node-5 (5), shippingservice-1 (4), emailservice (4), and cartservice
(4). Component-name variants such as suffixed replicas require an explicit
normalization/scoring decision.

Telemetry counts are physical CSV data lines (`wc -l` totals minus one header per
file). The preparation report must validate logical parsing, then report
kept/dropped rows and corrupt or multiline records.

## Relationship to the live database

The server PostgreSQL database was about 4.24 GB and contained 13,235,365 raw log,
4,710,165 raw metric, and 7,594,730 raw trace rows at audit time. Those database
counts are **not asserted to be this exact 70-case file snapshot**. The team must
document ingestion provenance and query/record linkage before combining the two
sources. All three `processed_*` telemetry tables were empty.

## Preparation and evaluation decisions still required

- Generate raw/kept/dropped row counts by modality, date, and preprocessing rule.
- Document Jira timezone, telemetry epoch units, window boundaries, and replica
  component normalization.
- Freeze a development/held-out query manifest before prompt or method tuning.
- Name the submitted method: simple deterministic z-score or full agent pipeline.
- Run real cases in the default dry-run mode first. Only the explicit
  `--write-database` mode writes investigations/telemetry, and it must target a
  disposable/local database for trial runs.
- Preserve per-case component, reason, timestamp, evidence, and scorer outcome.
