# EDA guide (M3) — exploring telemetry

Use [`../notebooks/01_eda_starter.ipynb`](../notebooks/01_eda_starter.ipynb) as your starting point.

## Questions to answer
- **Metrics:** which KPIs exist per component? What does "normal" vs "during a failure" look like?
- **Logs:** what do ERROR lines look like around a known failure? Common templates?
- **Traces:** which service calls which? Where does latency spike?
- **Ground truth:** open `record.csv` — what components/reasons appear? How are failures distributed?

## Steps
1. Load one day of `Market` telemetry (start with mock, then real).
2. Plot a KPI over time for 2-3 components; mark the failure window from `query.csv`.
3. Build a small **failure taxonomy**: group root-cause reasons into a few buckets.
4. Write `docs/` notes + numbers — these become the paper's **Dataset** section.

## Tips for newcomers
- Start tiny: one day, one component, one KPI. Then widen.
- Keep notebook cells short; clear outputs before committing.
