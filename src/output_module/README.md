# OUTPUT module — owner @thanhthanh278

**Job:** turn root-cause candidates into the final OpenRCA JSON + a human-readable report/plot.

**Contract:**
```python
build_output(candidates) -> Prediction      # Prediction.to_openrca_json() -> dict
save_prediction(pred, path)                 # writes JSON
render_report(pred) -> str                  # text report
```

**Files**
- `formatter.py` — build & save the OpenRCA-format JSON.
- `visualize.py` — `render_report()` (done) and `plot_component_kpi()` (**your TODO**).

**Beginner steps**
1. `python -m src.pipeline` and check the JSON keys match OpenRCA exactly.
2. Implement `plot_component_kpi()` to chart the failing KPI (use the EDA notebook as a guide).
3. M6/M7: build a small dashboard/report for the demo.
