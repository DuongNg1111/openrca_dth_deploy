# Research notes — OpenRCA (literature-review starter)

> Fill this in during **M2 (Literature Review)**. A skeleton is provided so newcomers know
> exactly what to capture. This file becomes the *Related Work* + *Background* of the paper.

## 1. The benchmark we build on
- **OpenRCA** (Xu et al., ICLR 2025): *Can LLMs Locate the Root Cause of Software Failures?*
  - 335 failures from 3 enterprise systems (`Telecom`, `Bank`, `Market`), **68 GB** telemetry.
  - Task: given a failure (time window + system) and its telemetry, output the **root cause
    component + reason + datetime**.
  - Telemetry = **metrics** (KPI time series) + **logs** (semi-structured text) + **traces**
    (dependency/call graphs).
  - Baseline = an **RCA-agent** that writes Python to query telemetry (avoids huge contexts).
  - Headline result: best model (Claude 3.5) solved only **~11.34%** → lots of room to improve.
- Our system targets the **Market** system, framed as **Logistics / Delivery Platform RCA**.

## 2. Reading list (each member reads >=2, writes a 5-line summary below)
- [ ] OpenRCA paper (everyone) — https://openreview.net/forum?id=M4qNIzQYpd
1/ OpenRCA paper 
**Title / venue / year**: OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures? / ICLR / 2025
**Problem**: While LLMs are effective in early software development stages, their ability to perform post-deployment Root Cause Analysis (RCA) on massive, heterogeneous telemetry data in complex systems remains largely under-explored
**Method (1-2 lines)**: The authors introduced OpenRCA, a goal-driven benchmark, and RCA-agent, a multi-agent system that uses program synthesis (Python) to analyze telemetry data programmatically, bypassing LLM context window limits
**Data used**: 335 real-world failure cases across three enterprise systems (Telecom, Bank, and Market) containing over 68 GB of telemetry data, including metrics, logs, and traces
**Result**: Current models struggle significantly; the best-performing model (Claude 3.5 Sonnet) achieved only 11.34% accuracy using the RCA-agent, and all models scored 0% on "Hard" tasks requiring all three root cause elements
**Why it matters for us / gap it leaves**: The research reveals that LLMs exhibit "reasoning laziness" (preferring shorter steps), struggle with non-natural language tokens (like GUIDs and error codes), and require higher error tolerance to effectively use execution feedback in agentic workflows

- [ ] An AIOps / RCA survey (e.g. "A Survey of AIOps for Failure Management")
- [ ] One paper on **log-based** anomaly detection (e.g. DeepLog)
- [ ] One paper on **trace-based** RCA / microservice fault localization
- [ ] One paper on **metric** anomaly detection (e.g. time-series change-point)

## 3. Gap & our angle (novelty brainstorm — pick in M5)
1. **Heuristic + LLM hybrid** that uses cheap statistical triage first and only calls the LLM on hard cases (cut cost/latency vs the pure-agent baseline).
2. **Trace-graph-aware retrieval** that walks the service dependency graph to localize the failing logistics service faster.
3. **Domain-transfer framing** of microservice RCA as a logistics fulfillment pipeline (order -> warehouse -> shipment -> tracking) and measure if domain priors help.

## 4. Glossary (metric / log / trace) — fill during M2/M3
- **Metric / KPI**: ...
- **Log**: ...
- **Trace / span**: ...
- **Root cause component**: ...
