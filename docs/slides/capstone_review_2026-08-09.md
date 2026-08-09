---
marp: true
title: DTH OpenRCA Capstone Review
description: Evidence-first presentation draft for the final capstone session
paginate: true
theme: default
---

# DTH OpenRCA

## Evidence-first capstone review

Root-cause analysis on the OpenRCA **Market / cloudbed-1** system

Team: DTH
Review branch: `codex/dth-capstone-review-2026-08-09`
Evidence freeze target: 15 August 2026

> Current claim: the repaired mock, metric-only loader, and multimodal full
> pipeline are reproducible locally. One controlled Gemini/database case localized
> the labeled replica, but no multi-case accuracy result exists yet.

---

# Problem and success criteria

Given an incident from Jira or a local `RawQuery`, plus Market metrics, logs,
and traces:

1. identify the root-cause component;
2. explain the failure reason with evidence;
3. report occurrence time when the question requires it;
4. preserve the investigation and result safely.

Final evaluation should report top-1/top-3 component accuracy, reason accuracy,
timestamp correctness, denominator, failures, latency, and LLM cost if Gemini is
in the measured path.

**A successful mock run or Jira connection is not real-case accuracy.**

---

# 1. Get the Data — verified server inventory

| Item | Verified state on 9 Aug 2026 |
|---|---|
| Target | Market `cloudbed-1` |
| Coverage | 2022-03-20 and 2022-03-21 |
| Files | 20 total telemetry/data files |
| Queries | 70 logical CSV rows (multiline instructions) |
| Records | 70 rows in `record.csv` |
| Modalities | Metric, log, trace |
| Local size on server | About 12 GB |

The live PostgreSQL raw tables separately held 13,235,365 logs, 4,710,165
metrics, and 7,594,730 traces. Do not assume those rows are the same exact
evaluation snapshot; document provenance and joins before using them.

CSV-aware parsing confirms 70 logical query rows, 70 records, 29 component
labels, and 15 failure reasons. The dataset card and 20-file manifest preserve
query/record checksums
and the class distribution. Physical CSV counts are 15.46M metric, 25.77M log,
and 18.16M trace data lines; logical parsing/cleaning counts remain required.

---

# 2. Prepare the Data

The full pipeline currently performs:

- Jira query parsing and incident-window construction;
- validated dataset override, multi-date path selection, and metadata indexing;
- metric/log/trace preprocessing and service linking;
- a deterministic three-modality evidence gate before persistence;
- investigation-context construction and explicit-opt-in database persistence.

The CLI and Python API are non-writing by default. Only exact
`dry_run=False`/`--write-database` permits writes; cross-midnight windows require
every covered date folder, and invalid/non-finite metric values fail before an
investigation can be created.

Evidence gaps to close:

| Check | Required report |
|---|---|
| Time semantics | Jira timezone, epoch units, inclusive window rules |
| Cleaning | Raw/kept/dropped rows per modality and reason |
| Ground truth | Exact query/record join and component/reason/time fields |
| Portability | Local `data_root`; no EC2-only hard-coded path |
| Leakage | Fixed held-out query IDs before model/prompt tuning |

The live `processed_logs`, `processed_metrics`, and `processed_traces` tables were
empty; the team must explain their intended role.

---

# 3. Explore the Data (EDA)

No executed real-data EDA is preserved in the current repository. The tracked
notebook is a four-cell mock starter with no output.

Required final figures:

1. queries/incidents by root component and reason;
2. file and row coverage by date, service, KPI, and modality;
3. missingness, duplicate rate, and timestamp-unit distribution;
4. one aligned metric/log/trace incident window;
5. telemetry coverage before and after preprocessing.

Also resolve documentation contradictions: the research notes say trace IDs are
absent while the tracked sample contains `trace_id` and `span_id`. Report the real
Market schema, not the five-row sample schema.

---

# 4. Analyze — choose the submitted method

Two different paths coexist:

| Path | Current behavior | Evidence state |
|---|---|---|
| Lightweight OpenRCA | Metric change-point z-score + fixed KPI/reason map | Mock + one metric-only real case reproduced |
| Full pipeline | Jira/local query + Market + PostgreSQL + modality agents + Gemini | One real multimodal local integration reproduced |

The team must name one submitted method and one baseline. If the full pipeline is
the proposed method, use the lightweight deterministic method as a baseline and
evaluate both on the same fixed real cases.

Do not mix their output contracts or present the richer architecture as evaluated
unless its predictions pass the scorer.

---

# Full-pipeline architecture

```text
Jira incident OR local RawQuery
     │ parse + validate time/context
     ▼
Market metric ─ log ─ trace telemetry
     │ preprocess + link services
     ▼
Three-modality evidence gate
     │ dry-run ends safely / explicit write continues
     ▼
InvestigationContext + PostgreSQL persistence
     │
metric agent ─ log agent ─ trace agent
     └───────────┬───────────┘
                 ▼
          Gemini reasoning agent
                 │
          evidence + RCA result
```

The deterministic evidence checker is now wired before the production write
boundary. It requires usable metric, log, and trace frames plus corresponding
metadata; it rejects empty, all-null, malformed, and non-finite metric evidence.
This is a software-safety result, not proof that the detector is accurate.

---

# Evaluation status

The current experiment runner evaluates one injected mock case. Baseline and
proposed configuration both use mock telemetry, and the evaluator does not score
timestamp correctness.

Therefore, as of this review:

- no verified real-case baseline accuracy;
- no verified proposed-method accuracy;
- no held-out split or ablation;
- no statistical comparison or failure analysis;
- no evidence-backed headline percentage.

One read-only **metric-only** loader check is now preserved: Market `task_6` expected
`shippingservice-1 / container read I/O load`; the detector placed a related
shipping-service instance only #4 and ranked `node-6.currencyservice2-0` first.
This is a method/instance-normalization failure, not a benchmark estimate.

A separate real metric+log+trace dry-run prepared 160,750 / 175,481 / 94,875
rows and passed the pre-write evidence gate without database writes. The same case
then completed all 22 steps only after explicit write/agent opt-in against a
loopback-only disposable database.

Required result table:

| Variant | Cases | Top-1 | Top-3 | Reason | Time | Latency/cost |
|---|---:|---:|---:|---:|---:|---:|
| Deterministic baseline | TBD | TBD | TBD | TBD | TBD | TBD |
| Full agent pipeline | TBD | TBD | TBD | TBD | TBD | TBD |

---

# Repaired local baseline

The review branch fixes the immediate reproducibility failures:

- invalid Python pseudocode replaced with explicit evidence contracts;
- missing Gemini SDK dependency declared;
- YAML LLM fields preserved while secrets stay in environment variables;
- documented mock quickstart restored;
- ordinary tests no longer prompt, call Jira/Gemini, or write PostgreSQL;
- focused query/config/evidence regressions added.

Verified repair-branch checks at review time:

```text
compileall:       PASS
ordinary pytest: 78 passed; 19 live/mutating modules explicitly skipped
mock CLI:        PASS; top candidate = order-service
metric-only:     PASS; task_6 truth ranked #4 (top-1 miss)
full dry-run:    PASS; 3 modalities, database_writes=false
full integration: PASS; local disposable DB + Gemini, 2 RCA rows
```

These verify software safety and real-data loading—not Market accuracy.

---

# Controlled full-pipeline evidence

One development case, ground truth
`shippingservice-1 / container read I/O load`:

| Evidence | Verified observation |
|---|---|
| Prepared telemetry | 160,750 metric; 175,481 log; 94,875 trace rows |
| Dry-run | Evidence `COMPLETE`; 68.18 s; no DB writes |
| Opt-in integration | 211.03 s; 1 investigation; 17 evidence; 2 RCA rows |
| Primary result | `shippingservice-1`; memory pressure → heavy reads → throttling |
| Reason scoring | Pending canonical mapping to `container read I/O load` |

The component localization matches this case. The free-text narrative mixes
memory exhaustion with the labeled read-I/O reason, so this is an integration
success—not a reason-accuracy claim. Gemini output is nondeterministic and the
case was inspected during development.

---

# UI and demo readiness

The code contains Streamlit login/forms and incident listing, but OAuth was not
configured on the audited host. The current report flow does not launch the RCA
pipeline or display a saved root cause, and several dashboard totals/status
messages are placeholders.

Final demo should use a controlled path:

1. select one fixed Market query and show its ground truth privately;
2. display the extracted telemetry window and counts;
3. run baseline, then the full method against a disposable/local database;
4. show ranked evidence and prediction;
5. reveal truth and scorer verdict;
6. open the preserved result artifact.

Fallback: saved run log/recording from the same commit. Label any mock or hardcoded
UI element clearly.

---

# Error analysis plan

For at least two failures and one representative success, show:

| Layer | Question |
|---|---|
| Data | Was the correct service covered in all modalities/window? |
| Preparation | Were units, time zone, and component names normalized? |
| Agents | Which modality supported or contradicted the prediction? |
| Reasoning | Did Gemini overrule stronger deterministic evidence? |
| Output | Did component/reason/time mapping match evaluator semantics? |

Classify failures before changing prompts or thresholds. Freeze the evaluation set
first, and keep all per-case outputs so improvements are auditable.

---

# Limitations and security

- One real-case runtime was measured; multi-case Market accuracy and cost were not.
- Full-pipeline writes are explicit opt-in and still must target the disposable
  local database before any live-server run.
- Portable CLI overrides now work, but tracked YAML still contains
  `/home/ubuntu/Market`; Streamlit OAuth was not configured on the host.
- Large SQL dumps were older than the live DB and are not current backups.
- Raw and processed DB table semantics need clarification.
- UI readiness messages cannot substitute for dependency health.
- LLM reasoning needs deterministic validation, failure handling, and cost/latency.

Security gate: keep `.env`, API tokens, passwords, PEM files, private endpoints,
DB dumps, and telemetry outside Git, slides, Slack, and screenshots.

---

# 5. Communicate the Results

Every claim should point to evidence:

| Claim | Required artifact |
|---|---|
| Market scope | Dataset card + checksum + manifest |
| Preparation quality | Before/after counts + schema report |
| Method behavior | Versioned configuration + architecture |
| Accuracy | Per-case predictions + scorer output |
| LLM benefit | Baseline/proposed comparison + ablation |
| Reproducibility | Fresh-run log + commit SHA |

Recommended 10–12 minute story:

**problem → Market data → preparation/EDA → deterministic baseline → full agent
method → controlled evaluation → errors → demo → limitations → next step**

Do not spend presentation time on unconnected UI screens at the expense of data,
method, or result evidence.

---

# Contribution ownership — complete before final

Do not infer ownership from the final branch. Each student must add evidence for
their own work before 15 August:

| Area | Named owner(s) | Evidence required |
|---|---|---|
| Data acquisition and schema | **Team to fill** | Original commit/PR + dataset notes |
| Preprocessing and time semantics | **Team to fill** | Tests + before/after counts |
| Metric/log/trace agents | **Team to fill** | Module commits + one traced case |
| Reasoning, persistence, and UI | **Team to fill** | Commit/PR + saved run/demo |
| Evaluation and presentation | **Team to fill** | Scorer artifact + slide owner |

The review commits repair and document the shared code; they do **not** establish
which student authored the original modules. Teacher evaluation should reconcile
the table with Git history and a short individual explanation.

---

# Completeness gate

- [x] Market dataset card plus 20-file byte/SHA-256 manifest.
- [ ] Real-data preparation report and executed EDA figures.
- [ ] One chosen submitted method, baseline, split, and metric definition.
- [x] Metric-only loader/time-window contract tested on one real case.
- [x] Full method run once against a disposable/local DB with no live write.
- [ ] Per-case result table, ablation, two failures, one success.
- [ ] UI/demo displays a real saved RCA or is scoped honestly.
- [ ] Fresh-clone setup/run log and dependency/config manifest.
- [ ] Citations, contributions, security, and limitations reviewed.

Completeness means that a teacher can trace dataset → query → telemetry → method
→ prediction → ground truth → score without receiving a secret.

---

# Conclusion and next steps

## What exists

A broad Jira/telemetry/database/agent implementation, a safe mock baseline, and
one controlled real multimodal integration run.

## What the evidence currently says

Software repair and one-case integration checks pass, but no multi-case Market
evaluation supports an accuracy claim yet.

## Before the final session

1. freeze a small held-out Market manifest;
2. generate preparation/EDA evidence;
3. choose baseline versus submitted method;
4. resolve/score replica normalization exposed by `task_6`;
5. score multiple frozen cases with canonical reason/component normalization;
6. preserve per-case outputs, model/version, latency, and cost.

---

# Appendix — reproducibility and citations

Record in the final deck:

```text
Repository: github.com/ThienHuynhNgoc/OpenRCA_DTH
Branch:     codex/dth-capstone-review-2026-08-09
Code commit: 3f99de3
Evidence commits through: 9a08ffd
Dataset:    docs/review/market_cloudbed1_file_manifest_2026-08-09.tsv
Dry run:    python -m src.full_pipeline --raw-query-file local-query.json \
              --data-root /absolute/path/to/Market --dataset cloudbed-1 \
              --timestamp-offset-hours 8
Integration: same command plus --write-database --run-agents, against a \
             disposable loopback-only PostgreSQL target
Results:    docs/review/full_pipeline_local_integration_2026-08-09.md
```

Primary sources:

- Microsoft OpenRCA repository: https://github.com/microsoft/OpenRCA
- OpenRCA paper, ICLR 2025: https://openreview.net/forum?id=M4qNIzQYpd

Add canonical citations for comparison methods. The upstream paper's reported
accuracy is not this team's accuracy.
