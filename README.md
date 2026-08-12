# OpenRCA_DTH — Logistics / Delivery Platform RCA

> Capstone built on **[microsoft/OpenRCA](https://github.com/microsoft/OpenRCA)** (ICLR'25):
> *Can Large Language Models Locate the Root Cause of Software Failures?*

We build an **LLM-assisted Root Cause Analysis (RCA)** system for a **Logistics** scenario.
Given a natural-language failure query (a time window + the system), the pipeline reads telemetry
(**metrics, logs, traces**) and outputs the **root cause component + reason** in OpenRCA's format.

```
User query ──▶ [ INPUT ] ──▶ [ PROCESS ] ──▶ [ OUTPUT ] ──▶ {"root cause component", "reason", "datetime"}
   (NL)         DEV 1           DEV 2            DEV 3
```

## The 3 modules = 3 developers
| GitHub | Suggested module | Folder |
| --- | --- | --- |
| @DuongNg1111 | Input module | `src/input_module` |
| @HoangNguyen2803 | Process module | `src/process_module` |
| @thanhthanh278 | Output module | `src/output_module` |

> The three modules talk to each other **only** through the dataclasses in
> [`src/schemas.py`](src/schemas.py). Agree on those shapes first; then each dev can work in parallel.

## Quickstart (works out of the box, no dataset needed)
```bash
python -m src.pipeline          # prints a sample OpenRCA-format prediction on MOCK data
python tests/test_pipeline_smoke.py   # or: python -m pytest -q
python experiments/run_experiment.py --config experiments/configs/baseline.yaml
```

To validate a local Market dataset without Jira, Gemini, or database writes,
save `issue_key`, `incident_description`, `environment`, `affected_system`, and
`incident_time` as a `RawQuery` JSON object and run:

```bash
python -m src.full_pipeline \
  --raw-query-file local-query.json \
  --data-root /path/to/Market \
  --dataset cloudbed-1 \
  --timestamp-offset-hours 8
```

This full-pipeline command is a dry run by default. Database persistence
requires the explicit `--write-database` flag, and agents additionally require
`--run-agents`. The Python `run_pipeline()` API is also non-writing by default;
programmatic persistence requires an explicit `dry_run=False`. `--dataset`
is treated as an explicit source override, and windows crossing midnight load
every covered date folder or fail with a missing-coverage error.

## Where to start (read these in order)
1. [`docs/00_capstone_handbook.md`](docs/00_capstone_handbook.md) — the whole journey, milestones, how Jira maps to the repo.
2. [`docs/01_git_workflow.md`](docs/01_git_workflow.md) — branch / commit / PR rules (read before you push anything!).
3. [`docs/02_environment_setup.md`](docs/02_environment_setup.md) — install Python + get the dataset.
4. [`CONTRIBUTING.md`](CONTRIBUTING.md) — code & documentation conventions.
5. Your module's README: `src/input_module/`, `src/process_module/`, `src/output_module/`.

## Target system & dataset
- OpenRCA system: **Market** (`dataset/Market/cloudbed-1`). See [`data/DATA.md`](data/DATA.md).
- Output format (OpenRCA):
```json
{ "1": { "root cause occurrence datetime": "2021-03-25 09:21:00",
         "root cause component": "order-service",
         "root cause reason": "high disk I/O read usage" } }
```

## Branching (PR-only `main`)
`main ⟵ staging ⟵ dev ⟵ feature/*` — default branch is **`dev`**. You **cannot push to `main`**;
open a Pull Request. Details in [`docs/01_git_workflow.md`](docs/01_git_workflow.md).

DUONG: test 1
TEST: Duong 
TEST: ThanhThanh
