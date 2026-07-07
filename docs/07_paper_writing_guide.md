# Paper writing guide (M7)

We aim for a short workshop-style paper. Each milestone already produced a piece of it.

## Suggested outline → which milestone feeds it
1. **Abstract / Intro** 
**Abstract**
•	Background: Failure management in modern microservice architectures has become increasingly complex due to the explosion of heterogeneous telemetry data, including metrics, logs, and traces.
•	Problem & Gap: Although Large Language Models (LLMs) offer a promising avenue for automated AIOps, recent state-of-the-art research (OpenRCA, 2025) reveals a severe performance bottleneck. Even the most capable models (e.g., Claude 3.5 Sonnet) coupled with program-synthesis agents achieve a mere 11.34% accuracy on real-world incidents. This failure is driven by "reasoning laziness" in multi-step tasks and an inability to process non-natural language tokens like GUIDs and error codes.
•	Proposed Method: In this work, we propose [Your Method Name, e.g., SmartRCA], an advanced multi-agent framework designed to bridge this 11% gap. We introduce two core novelties: (1) a Strict Reasoning Guardrail that mitigates LLM cognitive shortcuts, and (2) a Telemetry Context Enricher that translates low-level technical tokens into semantic, LLM-friendly context.
•	Results: Extensive evaluation on the Market dataset demonstrates that our framework significantly outperforms existing baselines, particularly on high-difficulty root cause localization tasks.
**Introduction**
•	Motivation: High availability and reliability are critical for large-scale distributed cloud systems. However, manual Root Cause Analysis (RCA) is highly time-consuming, leading to a high Mean Time to Resolution (MTTR).
•	Evolution of AIOps: The field has transitioned from traditional statistical and single-modal machine learning models (e.g., DeepLog for logs, RobustTAD for metrics) toward LLM-driven multi-modal data fusion.
•	The 11% Performance Gap: We analyze why existing code-driven RCA agents fail in production. The primary bottleneck lies in the cognitive gap between understanding natural language and reasoning over raw, interleaved telemetry data. LLMs exhibit "reasoning laziness," opting for shorter, incomplete diagnostic steps.
•	Our Angle: We present a novel orchestration layer that enforces structured execution feedback loops and context enrichment, tackling the core limitations highlighted by recent benchmarks.

2. **Related Work** 
**2.1 Traditional & Single-Modal AIOps**
•	Log-based Anomaly Detection: Pioneering frameworks like DeepLog (2017) utilize Long Short-Term Memory (LSTM) networks to model system logs as natural language sequences. While effective at detecting execution path deviations in real-time, they operate in isolation and ignore infrastructure-level hardware metrics.
•	Metric-based Anomaly Detection: Systems like RobustTAD leverage deep neural networks to learn temporal patterns across multivariate time series. They excel at identifying resource bottlenecks (e.g., CPU/Memory surges) under noisy workloads but lack the semantic capacity to explain why the anomaly occurred.
•	Trace-based Fault Localization: Approaches like MicroRCA (2020) construct attributed graphs to model anomaly propagation between microservices and hosts without requiring application-level instrumentation.
**2.2 LLM-based AIOps**
•	Following the comprehensive taxonomy from recent AIOps surveys (2024), Large Language Models have redefined failure management by providing cross-platform generality and cross-task flexibility, moving beyond rigid, rule-based traditional systems.
**2.3 LLM Agents for Code-driven RCA**
•	The OpenRCA (2025) framework introduced a goal-driven benchmark where agents use program synthesis (Python) to programmatically query telemetry data, bypassing context window limitations. This serves as the direct baseline for our proposed improvements.

3. **Problem & Data** 
**3.1 OpenRCA Task Definition**
The multi-modal Root Cause Analysis task is formulated as follows:
•	Input: An incident time window $T = [t_{\text{start}}, t_{\text{end}}]$ and a massive, heterogeneous telemetry dataset $\mathcal{D} = \{\mathcal{M}, \mathcal{L}, \mathcal{T}\}$, where $\mathcal{M}$, $\mathcal{L}$, and $\mathcal{T}$ represent metrics, logs, and traces, respectively.
•	Output: A root cause triplet $Y = (C, E, X)$, where:
o	$C \in \mathcal{C}$ is the faulty component (e.g., payment-service).
o	$E \in \mathcal{E}$ is the root cause element (e.g., Database Connection Pool Exhaustion).
o	$X$ is a human-readable text explanation detailing the failure propagation chain.
**3.2 Market Dataset Statistics**
Our empirical evaluation focuses heavily on the Market partition of the OpenRCA benchmark:
•	System Nature: A complex, production-grade e-commerce application built on a microservice architecture (comprising services such as Frontend, Cart, Inventory, and Shipping).
•	Data Scale: The dataset contains gigabytes of raw telemetry data, including high-frequency KPI metrics, interleaved concurrent logs, and end-to-end distributed transaction traces.
**3.3 Failure Taxonomy**
Incidents within the Market dataset are classified into three major operational categories:
•	Infrastructure/Resource Faults: CPU throttling, Out-Of-Memory (OOM) kills, and network packet loss.
•	Application/Logic Faults: Code bugs triggering HTTP 500 errors, infinite loops, and database connection timeouts.
•	Dependency/Cascading Faults: Downstream service latencies propagating upstream, causing widespread system degradation.

4. **Method** 
**4.1 Pipeline Architecture Overview**
The proposed pipeline flows as follows:
$$\text{Raw Telemetry Data} \rightarrow \text{Telemetry Parser \& Abstractor} \rightarrow \text{Multi-Agent RCA Orchestrator} \rightarrow \text{Root Cause Triplet } Y(C, E, X)$$
**4.2 Module Specifications & Our Novelty**
•	Novelty 1: Strict Chain-of-Thought (CoT) Guardrails: To counteract "reasoning laziness," the agent is forced into a deterministic three-phase cognitive loop: (1) Anomaly Symptom Extraction, (2) Hypothesis Graph Construction, and (3) Empirical Code Verification.
•	Novelty 2: Telemetry Token Enricher (Semantic Translation): Before telemetry strings are fed into the LLM, this module automatically resolves abstract hashes, GUIDs, and hexadecimal error codes into human-readable semantic definitions via a specialized lookup layer.
•	Novelty 3: Enhanced Execution Feedback Loop: We implement a robust self-correction prompt mechanism. If the agent's synthesized Python code execution fails or returns null results, the system feeds the runtime traceback error back into a debugging layer, allowing the agent to dynamically rewrite the queries.

5. **Experiments** 
**5.1 Experimental Setup**
•	Backbone Models: Evaluated using state-of-the-art LLMs including GPT-4o and Claude 3.5 Sonnet.
•	Evaluation Metrics: Exact Match Accuracy for the Faulty Component ($C$) and Root Cause Element ($E$), alongside semantic overlap metrics (BLEU/ROUGE) for the Explanation ($X$).
**5.2 Main Results**
Method	Backbone	Component Acc (%)	Element Acc (%)	Overall (Hard Tasks) Acc (%)
OpenRCA Baseline	Claude 3.5 Sonnet	~20.00%	~15.00%	11.34%
OpenRCA Baseline	GPT-4o	~18.00%	~12.00%	<10.00%
Our Proposed Method	Claude 3.5 Sonnet	[Your Target %]	[Your Target %]	[Your Target % (>11.34%)]
**5.3 Ablation Studies**
To verify the distinct contribution of each module, we perform three ablation variations:
•	Full Pipeline: Incorporates all proposed novelties.
•	w/o Strict CoT: Removes the reasoning guardrails to measure the impact of LLM "laziness."
•	w/o Token Enricher: Feeds raw GUIDs and error codes directly to the LLM to assess performance drop under non-natural language stress.
**5.4 Error Analysis**
We categorize remaining failure modes of our system, which primarily occur during:
•	Data Sparsity Cases: Missing or uncollected log blocks during critical system crashes, leaving insufficient empirical proof for the agent to verify its hypothesis.

6. **Conclusion & Limitations** — what worked, what's next.
**Conclusion**
•	This paper successfully addresses the 11.34% performance bottleneck identified in LLM-based post-deployment root cause analysis.
•	By enforcing structured reasoning guardrails and implementing a telemetry token semantic enricher, our framework significantly increases localization accuracy on the complex Market dataset, providing a viable path toward fully automated corporate AIOps.
**Limitations & Future Work**
•	Limitations: The multi-agent execution loop incurs relatively high token costs and inference latency due to the multi-turn code synthesis and debugging cycles.
•	Future Work: Future research will focus on knowledge distillation to fine-tune smaller, open-source models (e.g., Llama-3-8B) specialized in telemetry database querying, reducing operational costs while preserving reasoning accuracy.

## Our novelty candidates (pick & defend one)
1. **Heuristic + LLM hybrid** that uses cheap statistical triage first and only calls the LLM on hard cases (cut cost/latency vs the pure-agent baseline).
2. **Trace-graph-aware retrieval** that walks the service dependency graph to localize the failing logistics service faster.
3. **Domain-transfer framing** of microservice RCA as a logistics fulfillment pipeline (order -> warehouse -> shipment -> tracking) and measure if domain priors help.

## Writing tips for newcomers
- One claim per paragraph; back every claim with a number or a citation.
- Make figures first, then write around them.
- Reproducibility: the repo + `experiments/` + this guide *is* the appendix.
