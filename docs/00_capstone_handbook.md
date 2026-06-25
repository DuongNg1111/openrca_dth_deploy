# Capstone Handbook — OpenRCA_DTH

Welcome! This is your map for the whole project: from "we just cloned a repo" to "we wrote a paper".
Team theme: **Logistics / Delivery Platform RCA** (OpenRCA system: **Market**).

## The big idea
OpenRCA asks: *can an LLM find the root cause of a software failure from telemetry?* The best models
today solve only ~11%. **That gap is our opportunity.** We build a working RCA pipeline, then add one
**novel improvement**, run experiments, and write it up.

## The pipeline (and who owns what)
```
User query → [INPUT @DuongNg1111] → [PROCESS @HoangNguyen2803] → [OUTPUT @thanhthanh278] → root cause JSON
```
You work in parallel by respecting the contracts in `src/schemas.py`.

## Milestones (mirrored in Jira, project DEV)
| # | Milestone | Output |
| - | --------- | ------ |
| M1 | Foundations & Setup | everyone can run the pipeline; dataset downloaded |
| M2 | Literature Review | `RESEARCH.md` filled; reading summaries; novelty shortlist |
| M3 | Data & EDA | loaders + EDA notebook; failure taxonomy; dataset stats |
| M4 | Baseline & Pipeline | real-data pipeline + eval harness + baseline numbers |
| M5 | Novelty & Method | chosen idea implemented; method write-up |
| M6 | Experiments & Evaluation | baseline vs proposed vs ablations; figures/tables |
| M7 | Paper & Documentation | full draft + reproducibility package + demo |

## How Jira maps to this repo
- Each **milestone = an Epic** (per team) in Jira.
- Each **task** in Jira links to the file/folder you'll touch here.
- Tasks are **unassigned**; your **team leader assigns** them. Pick the task, move it to *In Progress*.

## How a normal week looks
1. Take a Jira task → make a `feature/*` branch off `dev`.
2. Code + docstring + a quick test/notebook cell.
3. Open a PR into `dev`, link the Jira issue, get 1 approval + green CI, merge.
4. Update the Jira task to *Done* and note what you learned.

## Path to the paper
Each milestone's output feeds a paper section — see `docs/07_paper_writing_guide.md`.
