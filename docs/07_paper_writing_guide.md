# Paper writing guide (M7)

We aim for a short workshop-style paper. Each milestone already produced a piece of it.

## Suggested outline → which milestone feeds it

| **Paper**   | **Title**                                                                                  | **Main Contribution**                                                                                                                                                                                        | **How We Use It in Our Project**                                                                                                                          |
|-------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Paper 1** | OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures? (ICLR 2025) | Introduces OpenRCA, a system that uses LLMs and Python programs to find the root cause of software failures by checking metrics, logs, and traces. It also provides a benchmark with 335 real failure cases. | This is the main paper for our project. We use its workflow and output format to build our own RCA system on the Market dataset.                          |
| **Paper 2** | A Survey of AIOps for Failure Management in the Era of Large Language Models (2024)        | Reviews how LLMs can help with failure management and compares them with traditional AIOps methods. It also explains current challenges and future research.                                                 | We use this paper to explain why LLMs are useful for failure management and why better RCA methods are needed.                                            |
| **Paper 3** | DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning (2017)     | Uses an LSTM model to learn normal log patterns and detect unusual log events in real time.                                                                                                                  | We use this paper as an example of log-based anomaly detection. It shows that using only logs is not enough for complete RCA.                             |
| **Paper 4** | MicroRCA: Root Cause Localization of Performance Issues in Microservices (2020)            | Uses service connections and system data to find where performance problems start in microservices.                                                                                                          | We use this paper to explain trace-based root cause analysis. It focuses on finding the faulty service but does not combine different types of telemetry. |
| **Paper 5** | RobustTAD: Robust Time Series Anomaly Detection for Multivariate Metrics                   | Uses deep learning to find unusual changes in system metrics like CPU, memory, and network usage.                                                                                                            | We use this paper as an example of metric-based anomaly detection. It can find abnormal metrics but cannot explain the root cause by itself.              |

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

| **Step** | **Details** |
|----------|-------------|
| **1. Receive User Query** | The user submits a failure report in natural language.<br><br>**Example:** *"Cannot create shipping order at 17:23:19."* |
| **2. Initialize AI Agents** | The system sends the user query to the LLM. The LLM initializes four specialized AI agents: **Log Agent**, **Metric Agent**, **Trace Agent**, and **Reasoning Agent**, each with a predefined role. |
| **3. Generate Lightweight Python Scripts** | The Log, Metric, and Trace Agents each generate a lightweight Python script (5–10 lines). Each script performs one small investigation task to retrieve the telemetry relevant to the reported incident. |
| **4. Execute the Investigation** | The generated Python scripts are executed by the system to retrieve the relevant Logs, Metrics, and Traces from the telemetry dataset. |
| **5. Analyze Individual Evidence** | Each analysis agent analyzes its retrieved telemetry, extracts important findings, and summarizes the evidence. |
| **6. Evidence Aggregation** | The Log, Metric, and Trace Agents send their summarized findings to the Reasoning Agent. |
| **7. Reasoning & Decision** | • **Validation:** Evaluates whether the collected evidence is sufficient to identify the root cause.<br><br>• **Conflict Resolution:** Resolves discrepancies between evidence types by prioritizing the most reliable evidence.<br><br>• **Targeted Refinement:** If the evidence is insufficient, the Reasoning Agent assigns a targeted follow-up investigation to the appropriate analysis agent(s), ensuring an efficient iterative investigation. |
| **8. Final Output** | Once sufficient evidence is collected, the Reasoning Agent outputs:<br>1. Root Cause Component<br>2. Failure Reason<br>3. Exact Datetime. |

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
