# Experiments guide (M6) — make it reproducible

## Structure
- `experiments/configs/*.yaml` — one file per experiment (baseline, proposed, ablations).
- `experiments/run_experiment.py` — runs the pipeline over cases, appends a row to
  `experiments/results/results.csv`.

## Run
```bash
python experiments/run_experiment.py --config experiments/configs/baseline.yaml
python experiments/run_experiment.py --config experiments/configs/proposed.yaml
```

## Rules for trustworthy results
- **Fix the seed** and log the exact config with every result.
- Change **one thing at a time** (that is an *ablation*).
- Report: accuracy on component, on (component+reason), and cost/latency if relevant.
- Keep a results table: `baseline | proposed | proposed − ablation`.

## Error analysis (this is where papers get good)
- Sample 10 failures the system got wrong. Categorize *why*. Add a small table to the paper.
