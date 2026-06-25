# Paper writing guide (M7)

We aim for a short workshop-style paper. Each milestone already produced a piece of it.

## Suggested outline → which milestone feeds it
1. **Abstract / Intro** — the 11% gap, our angle (M1/M2).
2. **Related Work** — `RESEARCH.md` summaries (M2).
3. **Problem & Data** — OpenRCA task + `Market` dataset stats + failure taxonomy (M3).
4. **Method** — the pipeline + our **novelty** (M4/M5).
5. **Experiments** — baseline vs proposed vs ablations, error analysis (M6).
6. **Conclusion & Limitations** — what worked, what's next.

## Our novelty candidates (pick & defend one)
1. **Heuristic + LLM hybrid** that uses cheap statistical triage first and only calls the LLM on hard cases (cut cost/latency vs the pure-agent baseline).
2. **Trace-graph-aware retrieval** that walks the service dependency graph to localize the failing logistics service faster.
3. **Domain-transfer framing** of microservice RCA as a logistics fulfillment pipeline (order -> warehouse -> shipment -> tracking) and measure if domain priors help.

## Writing tips for newcomers
- One claim per paragraph; back every claim with a number or a citation.
- Make figures first, then write around them.
- Reproducibility: the repo + `experiments/` + this guide *is* the appendix.
