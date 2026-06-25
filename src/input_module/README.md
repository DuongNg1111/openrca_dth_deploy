# INPUT module — owner @DuongNg1111

**Job:** turn the user's question + raw telemetry into a clean `InputContext`.

**Contract (do not break this):**
```python
build_input_context(query: str, config: dict) -> InputContext
# InputContext(raw_query, system, time_window, components_hint, telemetry)
# telemetry = {"metric": [...], "log": [...], "trace": [...]}
```

**Files**
- `query_parser.py` — NL query → time window (+ component hints). *Done for the demo; extend it.*
- `telemetry_loader.py` — `load_mock()` (done) and `load()` (**your TODO**: read real data).

**Beginner steps**
1. Run `python -m src.pipeline` and read the printed result.
2. Open `query_parser.py`; try changing `example_query` in `config/config.yaml` and re-run.
3. M3/M4: implement `load()` to read `data/Market/cloudbed-1/telemetry/...` with pandas,
   returning the same shape as `load_mock()`. Keep the contract identical so DEV 2/3 don't break.
