# Paper writing guide (M7)

We aim for a short workshop-style paper. Each milestone already produced a piece of it.

## Suggested outline → which milestone feeds it
**1. Abstract / Introduction**

**Background & Problem Statement**

Large-scale software systems continuously generate massive telemetry data (metrics, logs, and traces). When failures occur, Root Cause Analysis (RCA) becomes highly challenging because engineers must manually investigate heterogeneous telemetry collected from multiple system components. Traditional AIOps techniques are typically designed for individual tasks and therefore have limited generalization across platforms. Although Large Language Models (LLMs) have demonstrated promising capabilities in software engineering, they cannot directly analyze massive operational datasets due to context window limitations.

*Source*: Paper 1 – OpenRCA; Paper 2 – AIOps Survey

**Real-world Motivation**

For example, a logistics platform may fail during peak business hours, generating gigabytes of monitoring data. Engineers cannot manually inspect every log, metric, and trace, while an LLM cannot process the entire dataset simultaneously. Therefore, an automated framework is required to progressively investigate telemetry data and identify the underlying root cause.

*Source:* Paper 1 – OpenRCA

**Research Objective**

This project adopts the OpenRCA framework as the foundation for implementing a simplified prototype for automated Root Cause Analysis. The implementation focuses on the Market benchmark and aims to identify the Root Cause Component, Failure Reason, and Exact Datetime from heterogeneous telemetry data.

**2. Related Work**

**2.1 AIOps Frameworks**

LLM-based failure management offers greater flexibility across different operational tasks than conventional AIOps methods, although reliable deployment in production environments remains an open challenge.

*Source:* Paper 2 – AIOps Survey

**2.2 Log-based Anomaly Detection**

DeepLog applies LSTM networks to learn normal log sequences and detect anomalies. However, it only analyzes logs and cannot utilize metrics or traces.

*Source:* Paper 3 – DeepLog

**2.3 Trace-based Root Cause Localization**

MicroRCA models service dependencies using attributed graphs to localize fault propagation across microservices. Its primary focus is localization rather than heterogeneous telemetry integration.

*Source:* Paper 4 – MicroRCA

**2.4 Metric-based Anomaly Detection**

RobustTAD uses deep learning to detect anomalies from multivariate KPIs such as CPU and memory utilization. It identifies abnormal metrics but cannot explain the responsible component or failure reason.

*Source:* Paper 5 – RobustTAD

**Research Gap**

Previous methods analyze logs, metrics, or traces independently. OpenRCA addresses this limitation by integrating heterogeneous telemetry through program synthesis and execution feedback. Therefore, this project adopts the OpenRCA framework as the basis for implementing an LLM-assisted RCA prototype on the Market benchmark.

*Source:* Paper 1, Paper 3, Paper 4, Paper 5

**3. Problem & Data**

**Problem Definition**

The RCA system must identify three outputs: Root Cause Component, Failure Reason, and Exact Datetime. Unlike anomaly detection, RCA explains where, why, and when a failure originated.

*Source:* Paper 1 – OpenRCA

**Telemetry Data**

• Metrics: numerical KPIs (CPU, memory, disk, etc.).
• Logs: timestamped textual system events and errors.
• Traces: request propagation across distributed services.

*Source:* Paper 1, Paper 3, Paper 4, Paper 5

**Benchmark Dataset**

The OpenRCA benchmark contains 335 real-world failures across Telecom, Banking, and Market systems with over 68 GB of telemetry data. This project focuses on the Market benchmark.

*Source:* Paper 1 – OpenRCA

**4. Methodology**

**4.1 Existing vs. Agentic Methods**

Traditional approaches analyze only one telemetry source. OpenRCA instead employs an RCA-agent that repeatedly generates a Python program, executes it to retrieve telemetry evidence, analyzes the returned results, and continues the investigation until sufficient evidence has been collected.

*Source:* Paper 1, Paper 3, Paper 4, Paper 5

**4.2 Our Chosen Methodology**

Our project adopts the iterative investigation workflow proposed by OpenRCA. For implementation simplicity, the prototype focuses on the Market dataset while preserving the same evidence collection process.

Workflow:

1. Receive Failure Information.
2. Generate a Python program.
3. Execute the program and analyze returned evidence.
4. Repeat if additional evidence is required.
5. Output the Root Cause Component, Failure Reason, and Exact Datetime.

*Source:* Paper 1 – OpenRCA

**5. Experiments**

**Findings & Baseline Performance**

OpenRCA evaluates 335 real-world failures. Claude 3.5 Sonnet achieved the highest overall accuracy of 11.34%, indicating that automated RCA remains highly challenging.

*Source:* Paper 1 – OpenRCA

**Hard Case Evaluation**

All evaluated LLMs achieved 0% accuracy on hard cases requiring simultaneous identification of component, reason, and timestamp.

*Source:* Paper 1 – OpenRCA

**Discussion**

These findings demonstrate the necessity of iterative evidence retrieval for RCA despite the remaining reasoning limitations of current LLMs.

*Source:* Paper 1 – OpenRCA

**6. Conclusion & Limitations**

**Conclusion**

Traditional methods analyze logs, metrics, and traces independently. OpenRCA integrates heterogeneous telemetry within a unified LLM-assisted RCA framework. Accordingly, this project adopts OpenRCA as the foundation for implementing and evaluating an RCA prototype on the Market dataset.

*Source:* Paper 1, Paper 3, Paper 4, Paper 5

**Limitations**

• Low localization accuracy.

• Context window limitations.

• Challenges in integrating heterogeneous telemetry.

*Source:* Paper 1, Paper 2, Paper 3, Paper 4, Paper 5

## Our novelty candidates (pick & defend one)
1. **Heuristic + LLM hybrid** that uses cheap statistical triage first and only calls the LLM on hard cases (cut cost/latency vs the pure-agent baseline).
2. **Trace-graph-aware retrieval** that walks the service dependency graph to localize the failing logistics service faster.
3. **Domain-transfer framing** of microservice RCA as a logistics fulfillment pipeline (order -> warehouse -> shipment -> tracking) and measure if domain priors help.

## Writing tips for newcomers
- One claim per paragraph; back every claim with a number or a citation.
- Make figures first, then write around them.
- Reproducibility: the repo + `experiments/` + this guide *is* the appendix.
