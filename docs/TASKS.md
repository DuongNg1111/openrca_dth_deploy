# Task roadmap — OpenRCA_DTH (mirror of Jira project DEV)

Tasks live in **Jira** (project **DEV**, Epic per milestone, **per team**). They are created
**unassigned** — the **team leader assigns** them. This file is the human-readable mirror so you can
see the whole plan in the repo. Keep it roughly in sync with Jira.

Suggested module owners: input → @DuongNg1111, process → @HoangNguyen2803, output → @thanhthanh278.

## M1 — Foundations & Setup  (everyone, ~week 1, no/low-code)
- [ ] Accept the GitHub invite; clone the repo; read README + `docs/00`, `docs/01`.
- [ ] Install Python 3.10+ and the virtual env; run `python -m src.pipeline` and the smoke test.
- [ ] Learn the branch/PR flow by opening a tiny `docs/*` PR into `dev`.
- [ ] Download the OpenRCA `Market` dataset (see `data/DATA.md`).
- [ ] Set up the team's Jira board & communication.

## M2 — Literature Review
- [ ] Read the OpenRCA paper; fill the summary in `RESEARCH.md`.
- [ ] Read 3-5 AIOps/RCA papers (split per `docs/03`); add summaries.
- [ ] Write the metric/log/trace glossary.
- [ ] Shortlist 1-2 novelty ideas.

## M3 — Data & EDA
- [ ] Implement the real telemetry loader (`input_module/telemetry_loader.load`).
- [ ] Run the EDA notebook; profile KPIs / logs / traces.
- [ ] Build a failure taxonomy from `record.csv`; write dataset stats.

## M4 — Baseline & Pipeline
- [ ] Wire the 3 modules on real data; reproduce a baseline number.
- [ ] Stand up `src/eval/evaluate.py` + `experiments/run_experiment.py` on real cases.
- [ ] Record baseline results in `experiments/results/`.

## M5 — Novelty & Method
- [ ] Pick a novelty direction; design it (write the method section draft).
- [ ] Implement it in `detect.py` / `reasoner.py` (keep contracts stable).
- [ ] Sanity-check vs baseline.

## M6 — Experiments & Evaluation
- [ ] Define the experiment matrix (baseline vs proposed vs ablations).
- [ ] Run with fixed seeds + logged configs; collect tables/figures.
- [ ] Error analysis on 10 wrong cases.

## M7 — Paper & Documentation
- [ ] Draft the full paper (use `docs/07`).
- [ ] Polish the reproducibility package (README, scripts, configs).
- [ ] Prepare the final demo/presentation.
