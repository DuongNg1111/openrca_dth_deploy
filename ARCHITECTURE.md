# Architecture — OpenRCA_DTH

```
                          Logistics / Delivery Platform RCA
   ┌──────────────┐   InputContext   ┌────────────────┐  list[RootCauseCandidate]  ┌───────────────┐
   │  INPUT (DEV1)│ ───────────────▶ │ PROCESS (DEV2) │ ─────────────────────────▶ │ OUTPUT (DEV3) │
   │ parse query  │                  │ transform      │                            │ format JSON   │
   │ load metric/ │                  │ detect anomaly │                            │ visualize     │
   │ log/trace    │                  │ reason (LLM*)  │                            │ report        │
   └──────────────┘                  └────────────────┘                            └───────────────┘
                                                                                          │
                                                                                          ▼
                                                            {"root cause component", "reason", "datetime"}
```

## Data contracts (the only thing the 3 modules share) — `src/schemas.py`
- `InputContext`  : `raw_query, system, time_window, components_hint, telemetry`
  - `telemetry = {"metric": [...], "log": [...], "trace": [...]}` (list of row dicts in mock mode)
- `RootCauseCandidate` : `component, reason, occurrence_time, confidence, evidence`
- `Prediction` : `candidates: list[RootCauseCandidate]` + `.to_openrca_json()`

## Module responsibilities
| Module | Owner | Public entrypoint | In → Out |
| --- | --- | --- | --- |
| input | @DuongNg1111 | `input_module.build_input_context(query, config)` | `str, dict → InputContext` |
| process | @HoangNguyen2803 | `process_module.analyze(ctx)` | `InputContext → list[RootCauseCandidate]` |
| output | @thanhthanh278 | `output_module.build_output(candidates)` | `list → Prediction` |

The orchestrator is [`src/pipeline.py`](src/pipeline.py): `INPUT → PROCESS → OUTPUT`.
Evaluation lives in [`src/eval/evaluate.py`](src/eval/evaluate.py).

