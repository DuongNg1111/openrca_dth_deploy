"""Run the pipeline over a set of cases and log a results row.

Usage:
  python experiments/run_experiment.py --config experiments/configs/baseline.yaml
Works on mock data out of the box. In M6, replace MOCK_CASES with real OpenRCA
query.csv / record.csv rows.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import load_config  # noqa: E402
from src.eval.evaluate import score  # noqa: E402
from src.pipeline import run  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

MOCK_CASES = [
    {
        "query": "On 2021-03-25 between 09:00 and 09:30 the delivery-tracking service showed elevated errors. Identify the root cause component and the root cause reason.",
        "truth": {
            "root cause component": "order-service",
            "root cause reason": "high disk I/O read usage",
        },
    },
]


def load_exp(path):
    cfg = {"name": "baseline"}
    if not path:
        return cfg
    try:
        import yaml

        with open(path) as f:
            cfg.update(yaml.safe_load(f) or {})
    except Exception:
        cfg["name"] = os.path.splitext(os.path.basename(path))[0]
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    exp = load_exp(args.config)
    base = load_config()
    base.update({k: v for k, v in exp.items() if k in base})

    preds, truths = [], []
    for case in MOCK_CASES:
        first = run(case["query"], base).to_openrca_json().get("1", {})
        preds.append(first)
        truths.append(case["truth"])

    metrics = score(preds, truths, check_reason=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_csv = os.path.join(RESULTS_DIR, "results.csv")
    is_new = not os.path.exists(out_csv)
    with open(out_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["experiment", "n", "correct", "accuracy"])
        w.writerow([exp.get("name"), metrics["n"], metrics["correct"], metrics["accuracy"]])

    print("Experiment :", exp.get("name"))
    print("Prediction :", json.dumps(preds, ensure_ascii=False))
    print("Metrics    :", metrics)
    print("Wrote      :", out_csv)


if __name__ == "__main__":
    main()
