# Full-pipeline local integration — one controlled Market case

Evidence date: 2026-08-09, Asia/Ho_Chi_Minh. This run verifies that the repaired
22-step pipeline can load real Market metrics, logs, and traces, persist them to a
disposable local PostgreSQL database, call the configured Gemini agents, and save
RCA results. It is **one development case, not an accuracy estimate**.

The reviewed implementation is frozen in code commit `3f99de3` on branch
`codex/dth-capstone-review-2026-08-09`.

## Safety boundary

- Input came from a local `RawQuery` JSON file, so Jira was not contacted.
- PostgreSQL 16 listened only on `127.0.0.1:55432` in a rootless sandbox.
- The target database was created from the repaired tracked `schema.sql` and was
  named `openrca_capstone_review_20260809`.
- `POSTGRES_HOST`, `POSTGRES_PORT`, and `POSTGRES_DB` were overridden for this
  process. No student-server database write occurred.
- Gemini was contacted because `--run-agents` was explicitly selected. No secret
  value is recorded here.

The normal CLI remains dry-run/no-write by default. The two write-capable flags
below are appropriate only for a disposable database.

```bash
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=55432
export POSTGRES_DB=openrca_capstone_review_20260809

python -m src.full_pipeline \
  --raw-query-file local-query.json \
  --data-root /absolute/path/to/Market \
  --dataset cloudbed-1 \
  --timestamp-offset-hours 8 \
  --write-database \
  --run-agents
```

## Case and prepared evidence

| Field | Observed value |
|---|---|
| Dataset | Market `cloudbed-1` |
| Incident | 2022-03-20 09:09:06 incident-local time |
| Analysis window | 08:54:06–09:24:06 |
| Ground truth | `shippingservice-1 / container read I/O load` |
| Metadata selected | 5 metric, 2 log, and 1 trace files |
| Prepared metric rows | 160,750 |
| Prepared log rows | 175,481 |
| Prepared trace rows | 94,875 |
| Linked services | 16 |
| Pre-write evidence gate | `COMPLETE`, confidence 1.00 |

An otherwise identical full-pipeline dry-run completed first with database writes
disabled. It produced the same prepared row counts in 68.18 seconds with maximum
RSS of 524,740 KB.

## Persisted local evidence

The explicitly enabled integration run completed with exit code 0 in 211.03
seconds and used a maximum RSS of 583,840 KB. Read-only counts in the disposable
database immediately afterward were:

| Table | Rows |
|---|---:|
| `investigations` | 1 |
| `investigation_metrics` | 160,750 |
| `investigation_logs` | 175,481 |
| `investigation_traces` | 94,875 |
| `evidence_records` | 17 |
| `rca_results` | 2 |

## RCA output and interpretation

The pipeline selected two logical services:

| Service result | Agent conclusion | Confidence |
|---|---|---:|
| `shippingservice` | `shippingservice-1` reached its memory limit, followed by heavy `/dev/vda` reads, CPU load/throttling, and degraded response time | 95% |
| `checkoutservice` | The same resource-pressure chain propagated to product-catalog and checkout latency | 90% |

The primary result correctly localized the ground-truth replica
`shippingservice-1` and cited the labeled read-I/O evidence. However, its free-text
root cause starts with memory exhaustion and describes a causal chain rather than
emitting the canonical reason label `container read I/O load`. Therefore this run
is a component-level integration success, **not yet a verified reason-accuracy
success**. A deterministic scorer must normalize the agent output before the team
reports component/reason accuracy.

The log agents returned no explicit error logs for the selected services; metric
and trace evidence drove the conclusions. Gemini output can vary, so preserve the
exact output, model/configuration, cost, and latency for every scored case.

## What this does and does not prove

This proves real multimodal loading, the pre-write evidence gate, current schema
compatibility, local persistence, agent invocation, reasoning, and result saving
for one controlled case. It does not prove held-out accuracy, reason-label
calibration, statistical reliability, UI readiness, or safe operation against the
live student database.
