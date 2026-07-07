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
- 1/ OpenRCA paper (everyone) — https://openreview.net/forum?id=M4qNIzQYpd

  **- Title / venue / year: OpenRCA**: Can Large Language Models Locate the Root Cause of Software Failures? / ICLR / 2025

  **- Problem**: While LLMs are effective in early software development stages, their ability to perform post-deployment Root Cause Analysis (RCA) on massive, heterogeneous telemetry data in complex systems remains largely under-explored

  **- Method (1-2 lines)**: The authors introduced OpenRCA, a goal-driven benchmark, and RCA-agent, a multi-agent system that uses program synthesis (Python) to analyze telemetry data programmatically, bypassing LLM context window limits

  **- Data used**: 335 real-world failure cases across three enterprise systems (Telecom, Bank, and Market) containing over 68 GB of telemetry data, including metrics, logs, and traces

  **- Result**: Current models struggle significantly; the best-performing model (Claude 3.5 Sonnet) achieved only 11.34% accuracy using the RCA-agent, and all models scored 0% on "Hard" tasks requiring all three root cause elements

  **- Why it matters for us / gap it leaves**: The research reveals that LLMs exhibit "reasoning laziness" (preferring shorter steps), struggle with non-natural language tokens (like GUIDs and error codes), and require higher error tolerance to effectively use execution feedback in agentic workflows
- 2/ An AIOps / RCA survey:

  **- Title / venue / year**: A Survey of AIOps for Failure Management in the Era of Large Language Models / arXiv (cs.SE) / 2024.

  **- Problem**: As software systems grow more intricate, traditional Artificial Intelligence for IT Operations (AIOps) methods used for failure management face significant challenges, specifically a lack of cross-platform generality and cross-task flexibility.

  **- Method (1-2 lines)**: This paper provides a comprehensive survey defining AIOps tasks and exploring how Large Language Models (LLMs) can be applied to various subtasks within failure management. It contrasts these LLM-based approaches with traditional AIOps methodologies to highlight advancements and differences.

  **- Data used**: The survey analyzes existing data sources for AIOps and reviews the diverse LLM-based approaches currently being adopted in the field.

  **- Result**: The survey establishes a detailed definition of AIOps tasks, identifies specific LLM-based approaches suitable for different subtasks, and outlines the current challenges and future directions for the domain.

  **- Why it matters for us / gap it leaves**: This work is critical because there was previously no comprehensive survey discussing the differences between LLM-based AIOps and traditional methods. It serves as a foundational guide for further development and application of LLMs to ensure high availability and reliability in large-scale distributed systems.

- 3/ One paper on **log-based** anomaly detection

  **- Title / venue / year**: DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning / CCS’17 (ACM Conference on Computer and Communications Security) / 2017.

  **- Problem**: As systems become more complex, traditional anomaly detection methods (such as PCA or invariant mining) are no longer effective at handling the massive volumes of unstructured, concurrent log data produced by modern applications. Existing methods often operate offline, require manual rules, or cannot effectively model the long-term dependencies in log sequences.

  **- Method (1-2 lines)**: DeepLog uses a Long Short-Term Memory (LSTM) neural network to model system logs as a natural language sequence, allowing it to automatically learn normal patterns and detect deviations in both execution paths and parameter values in real-time.

  **- Data used**: The study conducted extensive evaluations using large-scale log datasets from HDFS (over 11 million entries), OpenStack (1.3 million entries), and Blue Gene/L supercomputer logs (4.7 million entries).

  **- Result**: DeepLog achieved nearly 100% detection accuracy on HDFS logs while training on less than 1% of normal data. It significantly outperformed traditional methods like PCA and Invariant Mining, reaching F-measures of 96% to 98% across different datasets while maintaining a low prediction cost of roughly 1 millisecond per log entry.

  **- Why it matters for us / gap it leaves**: It is a pioneering general-purpose framework that provides online, log-entry level detection and supports automated workflow construction for diagnosis, even in systems with interleaved logs from concurrent tasks. However, the paper notes a gap in integrating data from multiple heterogeneous systems (e.g., combining database logs with disk logs) for more comprehensive diagnosis, which remains a goal for future work.

- 4/ One paper on **trace-based** RCA / microservice fault localization

  **- Title / venue / year**: MicroRCA: Root Cause Localization of Performance Issues in Microservices / Published in a conference (Communication Dans Un Congrès) / 2020.

  **- Problem**: Diagnosing performance issues in microservice architectures is highly challenging due to technological heterogeneity, the vast number of microservices, and frequent updates made to both software features and the underlying infrastructure.

  **- Method (1-2 lines)**: MicroRCA utilizes an attributed graph to model how anomalies propagate between services and hosts, allowing it to correlate application performance symptoms with real-time system resource usage without requiring any application-level instrumentation.

  **- Data used**: The approach was evaluated by injecting common faults and anomalies into a microservice benchmark running within a Kubernetes cluster.

  **- Result**: The experimental results indicate that MicroRCA is capable of accurately identifying the root causes of performance issues in complex microservice environments.

  **- Why it matters for us / gap it leaves**: This work is important because it offers a way to perform real-time root cause localization without the need for developers to modify their code for monitoring, which significantly reduces operational overhead. (Note: The provided sources do not explicitly detail the specific gaps or limitations left by this research.)

- 5/ One paper on **metric** anomaly detection

  **- Title / venue / year**: RobustTAD: Robust Time Series Anomaly Detection for Multivariate Metrics

  **- Problem**: Detect anomalies from large-scale multivariate system metrics in cloud services, where noisy telemetry and changing workloads make threshold-based methods unreliable.

  **- Method**: Learns temporal patterns and correlations among multiple metrics using a deep neural network, then detects anomalies based on deviations from learned normal behavior. Designed to be robust against noise and missing values in production monitoring data.

  **- Data used**:
  - Real-world cloud service monitoring metrics (CPU, memory, disk, network, latency, throughput, etc.)
  - Public multivariate time-series anomaly detection benchmarks

  **- Result**:
  - Achieved higher precision and F1-score than statistical and traditional machine learning baselines.
  - Reduced false positives while maintaining high recall on complex multivariate metric anomalies.

  **- Why it matters for us / gap it leaves**:
  - Why it matters: Metric anomaly detection is the first step in an RCA pipeline. RobustTAD can identify which KPIs become abnormal within the queried time window, providing strong evidence for downstream root cause reasoning.
  - Gap: The method only determines which metrics are anomalous. It does not correlate anomalies with logs or traces, infer the faulty component, or generate a human-readable root cause explanation. These limitations motivate our LLM-assisted RCA system, which integrates metrics, logs, and traces and outputs the root cause component and explanation in OpenRCA's format.

## 3. Gap & our angle (novelty brainstorm — pick in M5)
1. **Heuristic + LLM hybrid** that uses cheap statistical triage first and only calls the LLM on hard cases (cut cost/latency vs the pure-agent baseline).
2. **Trace-graph-aware retrieval** that walks the service dependency graph to localize the failing logistics service faster.
3. **Domain-transfer framing** of microservice RCA as a logistics fulfillment pipeline (order -> warehouse -> shipment -> tracking) and measure if domain priors help.

## 4. Glossary (metric / log / trace)

### Metric / KPI

**Definition:**
A metric is a numerical measurement used to monitor the performance or health of a system. A KPI (Key Performance Indicator) is a metric used to evaluate whether the system meets its expected objectives.

**Example (from dataset):**
- Timestamp: 1647767561
- Level: node
- Component: node-4
- Reason: node CPU spike
- Datetime: 2022-03-20 17:12:41

This event shows that **node-4** experienced a **CPU spike**, indicating abnormal resource utilization. Such performance indicators can be used as metrics to detect system anomalies.

---

### Log

**Definition:**
A log is a timestamped record of an event generated by the system during execution. It records information about system activities, warnings, and failures.

**Example (from dataset):**
- Timestamp: 1647768199
- Level: service
- Component: paymentservice
- Reason: container process termination
- Datetime: 2022-03-20 17:23:19

This record indicates that the **paymentservice** experienced a **container process termination**, which is an abnormal event that can be investigated during Root Cause Analysis.

---

### Trace / Span

**Definition:**
A trace records the complete path of a request through multiple services in a distributed system. A span represents a single operation within that trace.

**Example (based on related events in the dataset):**
- 2022-03-20 17:12:41 → node-4 → node CPU spike
- 2022-03-20 17:23:19 → paymentservice → container process termination

Although the dataset does not contain **trace_id** or **span_id**, these related events could belong to the same failure scenario. In a tracing system, the entire request path would be represented as a **trace**, while each service execution along the path would be a **span**.

---

### Root Cause Component

**Definition:**
The root cause component is the system component responsible for the original failure that causes other components to fail.

**Example (from dataset):**
- Timestamp: 1647767561
- Level: node
- Component: node-4
- Reason: node CPU spike
- Datetime: 2022-03-20 17:12:41

If services running on **node-4** later experience failures, such as **paymentservice** with **container process termination** at **2022-03-20 17:23:19**, then **node-4** can be identified as the root cause component because the infrastructure problem occurred before the service failure.
