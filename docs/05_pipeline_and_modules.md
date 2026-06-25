# Pipeline & modules — how the code fits together

```
input_module.build_input_context(query, config) -> InputContext
process_module.analyze(ctx)                      -> list[RootCauseCandidate]
output_module.build_output(candidates)           -> Prediction  (.to_openrca_json())
```
Orchestrated by `src/pipeline.py`. Contracts live in `src/schemas.py` — **never change a contract
without telling the other two devs.**

## Going from mock to real data (M4)
1. **INPUT:** implement `telemetry_loader.load()` to read `data/Market/cloudbed-1/telemetry/{date}`.
   Return the same dict shape as `load_mock()`.
2. **PROCESS:** point `analyze()` at the real features; improve `detect.py` / `reasoner.py`.
3. **OUTPUT:** confirm the JSON matches OpenRCA exactly; add plots in `visualize.py`.
4. Set `use_mock: false` in `config/config.yaml`.

## Evaluation
`src/eval/evaluate.py` compares predictions to `record.csv` ground truth → accuracy.
Run a full sweep with `experiments/run_experiment.py`.

## The contract test
`tests/test_pipeline_smoke.py` must stay green. If you change a contract, update it.
