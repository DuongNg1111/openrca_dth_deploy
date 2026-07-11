# Paper writing guide (M7)

We aim for a short workshop-style paper. Each milestone already produced a piece of it.

## Suggested outline → which milestone feeds it
**1.Abstract / Intro** 

**Content:** When large-scale software systems (such as telecom networks or banking platforms) crash after deployment, pinpointing the exact faulty component and its underlying cause is extremely difficult due to the massive volume of generated monitoring data.

**Problem:** Traditional approaches lack generality across different platforms and flexibility across tasks. Meanwhile, Large Language Models (LLMs), despite their proficiency in early code generation, remain largely under-explored in post-deployment Root Cause Analysis (RCA) and easily suffer from context window limitations when forced to read massive datasets.

**Real-World Example:** A food delivery platform crashes during peak hours, generating over 68 GB of telemetry data. Engineers cannot manually sift through it, and standard LLMs cannot process this massive file size at once due to context limits.

*Sources*: Paper 1 (OpenRCA ICLR 2025) & Paper 2 (AIOps Survey 2024).

**2. Related Work**

Prior research has attempted to detect and manage system failures through four main distinct directions:

**Direction 1 - Comprehensive Survey:** Defines automated IT operations (AIOps) tasks and explores how LLMs can replace traditional methods to ensure high system availability and reliability.

*Source:* Paper 2 (AIOps Survey 2024).

**Direction 2 - Log-based Anomaly Detection:** Models system logs as natural language sequences using AI to learn normal behaviors and flag real-time deviations in system execution paths.

*Source:* Paper 3 (DeepLog 2017).

**Direction 3 - Trace-based Fault Localization:** Uses graphs to model how anomalies propagate between microservices and physical hosts without requiring developers to modify application source code.

*Source:* Paper 4 (MicroRCA 2020).

**Direction 4 - Metric Anomaly Detection:** Utilizes deep learning to learn temporal patterns and correlations among multivariate metrics (e.g., CPU, Memory), detecting anomalies based on deviations from learned normal baselines even in noisy cloud environments.

*Source:* Paper 5 (RobustTAD).

**3. Problem & Data**

**Task:** Given a system failure within a specific time window, the system must output exactly three core elements: Root Cause Component + Failure Reason + Exact Datetime.

**Telemetry Data Types Used:** Consists of three primary sources:

**a. Metrics / KPIs:** Numerical health measurements. Example: Node-4 experiences a sudden CPU spike (node CPU spike).

**b. Logs:** Timestamped text event records. Example: The payment service container process abruptly shuts down (container process termination).

**c. Traces:** The execution path of a request across services. Example: Timeline analysis showing Node-4 failing first at 17:12, subsequently causing the payment service to crash at 17:23.

**Benchmark Dataset:** OpenRCA contains 335 real-world failure cases across 3 enterprise systems (Telecom, Bank, Market) totaling 68 GB of telemetry data.

*Source:* Paper 1 (OpenRCA ICLR 2025).

**4. Method / Solutions**

**A. Existing Methods from Literature:**

**Method 1 - Attributed Graph for Traces (MicroRCA):** Maps out structural service dependencies to track how performance anomalies propagate from physical infrastructure up to application services. (Source: Paper 4).

**Method 2 - LSTM Networks for Logs (DeepLog):** Treats log entries like natural language sentences, utilizing Long Short-Term Memory (LSTM) networks to detect execution path anomalies. (Source: Paper 3).

**Method 3 - Deep Learning for Metrics (RobustTAD):** Evaluates multi-variable time-series data using deep neural networks to pinpoint anomalous KPI behavior amid production noise. (Source: Paper 5).

**Method 4 - Multi-Agent & Execution Feedback (OpenRCA):** Employs program synthesis (writing Python scripts) to programmatically query telemetry data, bypassing context constraints. (Source: Paper 1).

**B. OUR CHOSEN METHODOLOGY (Divide and Conquer Framework):**

Our group will adopt Method 4 (Based on OpenRCA), narrowing the project scope strictly to the Market system (framed as a Logistics / Delivery Platform).

To resolve the core paradox where "the LLM is too lazy to reason but is forced to write/check code," we implement a "Divide and Conquer" execution feedback workflow. Instead of forcing the LLM to write one massive, complex 100-line script (which triggers reasoning laziness and brittleness upon bugs), we break the task into a series of micro-steps. The LLM may write 1,000 lines of code in total, but it executes them iteratively in tiny, ultra-simple 10-line blocks.

Our Step-by-Step Iterative Workflow:

**Step 1 (Micro-Code Generation):** The LLM writes a very short, dead-simple Python script (e.g., 5-10 lines using pandas) just to perform one basic check (e.g., filtering logs for a specific 5-minute window).

**Step 2 (Instant Execution Feedback):** Because the code is ultra-short, it is highly unlikely to fail. If a minor bug occurs, the LLM fixes it instantly in one second because it only has to read 5 lines of code (overcoming code-correction laziness).

**Step 3 (Micro-Reasoning & Dynamic Progression):** The script executes successfully and returns one lightweight, filtered clue. The LLM performs a tiny bit of reasoning on this single clue, and uses it to write the next 5-10 lines of simple code to dig deeper.

**Step 4 (Final Clean Output to User):** This loop repeats until all noisy data from the 68 GB pool is systematically eliminated. At the final step, the exact root cause is cleanly exposed on the screen. The LLM effortlessly extracts this clear evidence and outputs the exact 3 metrics required by the user.

**Real-World Project Example:**

**Input:** A customer reports an inability to create a shipping order on the Logistics platform at 17:23:19.

**Iteration 1:** LLM writes 5 lines of code to check delivery-service logs at 17:23. Output: Service crashed because it lost connection to Node-4.

**Iteration 2:** LLM writes 5 lines of code to check what happened to Node-4 earlier. Output: Node-4 CPU spike at 17:12:41.

**Final Output to User:** The LLM gathers these clear stepping stones and outputs the clean diagnostic summary:

Root Cause Component: node-4

Reason: node CPU spike

Datetime: 2022-03-20 17:12:41

**5. Experiments**

**General Finding:** State-of-the-art LLMs struggle heavily with post-deployment automated root cause localization.

**Empirical Results:** The best-performing setup (Claude 3.5 Sonnet equipped with the Python-writing RCA-agent) solved only 11.34% of the total failure cases.

**Hard Task Results:** On "Hard" cases—where the model must correctly identify all three elements (component, reason, and datetime) simultaneously—all tested LLM configurations scored an absolute 0% accuracy.

*Source:* Paper 1 (OpenRCA ICLR 2025).

**6. Conclusion & Limitations**

**Conclusion:** There remains a massive research gap in automated RCA using LLMs. While traditional tools like DeepLog or RobustTAD are excellent at detecting standalone anomalous logs or metrics, they cannot correlate or explain them. Frameworks like OpenRCA are necessary to aggregate multi-source data and translate it into human-readable diagnostics.

*Sources:* Paper 3 (DeepLog 2017) & Paper 5 (RobustTAD).

**Limitations**

**Reasoning Laziness** LLMs are prone to shortcutting; when presented with complex, multi-step clues all at once, they tend to guess superficial surface-level causes rather than reasoning deep.

**Token Vulnerability** LLMs struggle to process non-natural language tokens, meaning they frequently misinterpret or overlook complex GUIDs (Globally Unique Identifiers) and raw system error codes.

**Brittleness:** Without an enforced, micro-step execution feedback loop, an LLM agent will immediately give up or hallucinate answers the moment a monolithic piece of code throws a runtime error.

**Heterogeneous Data Silos:** Older methodologies (such as DeepLog) fail to integrate heterogeneous data sources, meaning they cannot cross-analyze database logs with physical disk logs simultaneously.

*Sources:* Paper 1 (OpenRCA ICLR 2025) & Paper 3 (DeepLog 2017).

## Our novelty candidates (pick & defend one)
1. **Heuristic + LLM hybrid** that uses cheap statistical triage first and only calls the LLM on hard cases (cut cost/latency vs the pure-agent baseline).
2. **Trace-graph-aware retrieval** that walks the service dependency graph to localize the failing logistics service faster.
3. **Domain-transfer framing** of microservice RCA as a logistics fulfillment pipeline (order -> warehouse -> shipment -> tracking) and measure if domain priors help.

## Writing tips for newcomers
- One claim per paragraph; back every claim with a number or a citation.
- Make figures first, then write around them.
- Reproducibility: the repo + `experiments/` + this guide *is* the appendix.
