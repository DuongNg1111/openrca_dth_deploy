# PROCESS module — owner @HoangNguyen2803

**Job:** from `InputContext`, find the most likely root-cause component(s) and explain why.

**Contract:**
```python
analyze(ctx: InputContext, top_k: int = 1) -> list[RootCauseCandidate]
```

**Files**
- `transform.py` — aggregate telemetry into per-(component,kpi) series.
- `detect.py` — anomaly detection + ranking. **The heart of the project.**
- `reasoner.py` — convert anomalies into readable reasons (optionally with an LLM).

**Beginner steps**
1. Run `python -m src.pipeline`; confirm it points at `order-service`.
2. Read `detect.py` — understand the change-point z-score.
3. M5 (novelty): improve detection (better stats, log/trace signals, or an LLM reasoner).
   Keep the `analyze()` contract stable so DEV 1/3 don't break.
