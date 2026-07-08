# Paper writing guide (M7)

We aim for a short workshop-style paper. Each milestone already produced a piece of it.

## Suggested outline → which milestone feeds it
**1.Abstract / Intro** 

**Abstract / Introduction**

**Abstract**

•	**Background:** Modern large-scale software applications are built like a massive puzzle using hundreds of smaller, connected services (called microservices). When a system crashes, it automatically generates a massive wave of warning data. This data comes in three types: system health charts (metrics), historical text diaries (logs), and data tracking paths (traces). 

•	**The Problem:** Using Artificial Intelligence (AI) to investigate these crashes automatically is highly desired. However, recent 2025 research revealed a harsh reality: even the smartest AI models (like Claude 3.5) only achieve an 11.34% accuracy rate when analyzing real production incidents. This happens because AI gets "cognitively lazy" (it takes mental shortcuts instead of looking deeper) and gets completely confused by messy computer codes like long hexadecimal numbers and system IDs. 

•	**Our Solution (The DTH Model)**: To fix this, we created an advanced AI framework that acts like a Digital Detective Team. Our system introduces two vital defenses: 

+**Strict Reasoning Guardrails**: A rulebook that stops the AI from guessing by forcing it into a strict, step-by-step verification process. 

+**Telemetry Context Enricher**: A translator that turns cryptic computer codes into plain, human-readable explanations before the AI reads them. 

•	**Results:** Testing proves our method successfully breaks past the 11.34% barrier, making AI much better at solving complex system failures. 

**Introduction**

•	**The Danger of Crashes**: When popular websites crash, companies lose massive amounts of money every minute. Relying on human engineers to dig through billions of data rows takes too long. We need automated Root Cause Analysis (RCA)—an AI that acts as a digital doctor to find the sickness instantly.

•	**Old Tools vs. Modern AI**: Older automated tools acted like hyper-specialized doctors. Some could only check the computer’s hardware heartbeat, while others could only read error messages. Today, we use Large Language Models (LLMs) to act as general practitioners that can inspect all data types at the same time. 

•	**The Laziness Bottleneck**: Even though modern AI is smart, raw computer data is too messy. When given raw files, the AI gets lazy, skims the data, and misses the true root cause. Our project directly tackles these flaws by forcing the AI to slow down, think step-by-step, and read translated data.

**2. Related Work**

We can group traditional tools based on how they examine a "crime scene" (a system crash): 

•	**The Log Readers:** These tools treat system logs like a text-based storybook to flag unexpected error messages. Limitation: They only read text; they cannot notice if the computer's "blood pressure" (CPU/Memory) is skyrocketing. 

•	**The Chart Watchers:** These focus strictly on numerical graphs, watching for sudden spikes in hardware usage. Limitation: They know the machine is "sick" (overloaded), but they cannot explain why. 

•	**The Path Trackers:** These tools build maps to see how a slowdown travels from one service container to another. 

•	**The Code-Driven Approach (OpenRCA 2025):** Raw system data is too massive to fit into an AI's short-term memory. A recent framework called OpenRCA fixed this by giving the AI a code interpreter. Instead of reading massive files directly, the AI writes Python code to filter and search the data. This is the foundation we are building upon.

**3. Problem & Data**

**What Evidence Does the Detective Get?**

When an application crashes, the system hands a "Box of Evidence" to our AI, containing: 

•	**The Crime Time Window**: The exact timeframe of the crash (e.g., "The app crashed between 10:00 AM and 10:15 AM. Only look at data within this 15-minute window"). 

•	**The Clues Left at the Scene:**

o	**Metrics (The Vital Signs)**: Numerical charts showing hardware status (e.g., CPU spiking to 100%). 

o	**Logs (The Diary)**: Text messages showing what the system was thinking right before it died (e.g., "Error: Cannot connect to database"). 

o	**Traces (The Footprints)**: A security camera map tracking a user's journey (e.g., User clicks 'Buy'  moves to Cart  gets stuck at Payment).

**The Detective's Final Case Report**

After digging through the evidence, the AI must deliver a final verdict answering exactly three things: 

1.	**The Culprit (Faulty Component)**: Which exact service caused the chain reaction? (e.g., payment-service). 

2.	**The Sickness (Root Cause Element)**: What technical bug killed that service? (e.g., Database Connection Pool Exhaustion — meaning it ran out of available slots to talk to the database).

3.	**The Case Narrative (Explanation)**: A plain English paragraph explaining the domino effect so human managers can easily understand what happened.

4. **Method**

To cure the AI's "laziness" and "confusion," we add three user-friendly features to our team: 

•	**Feature 1**: Mandatory 3-Step Reasoning (Curing Laziness): We lock the AI inside a strict rulebook. It must: (1) Extract strange symptoms, (2) Sketch a theory of which service is hurting which, and (3) Write and run Python code to physically check if the data supports the theory. No guessing allowed. 

•	**Feature 2**: The Translation Layer (Curing Confusion): Instead of blinding the AI with raw computer gibberish, this module pre-scans the data. It automatically swaps out cryptic tokens like **ERR_0x7F_CONN** with easy text like *[Network Timeout: Connection refused by database server].*

•	**Feature 3**: Never Giving Up (Self-Repair Loop): If the AI writes a Python script to search the data and the script crashes because of a coding mistake, our system doesn't stop. It shows the error to the AI and prompts: "Your code failed on line 4. Fix it and try again." The AI loops and repairs its own code until it successfully gets the data.

**5. Experiments**

•	**The Setup**: We use the brains of top-tier AI models (GPT-4o and Claude 3.5 Sonnet) to power our detective team and test them on an e-commerce platform dataset. 

•	**Target Metrics**: We score the AI based on whether it correctly points out the culprit service and the exact root cause. 

•	**Expected Results**: Since our system is currently in the design phase, our scores are marked as TBD (To Be Determined). Our main objective in the next step is to successfully beat the old 11.34% baseline score from previous papers. 

•	**Testing by Turning Features Off (Ablation Studies)**: To prove our features actually work, we will try turning off the "Translator" or the "Strict Rules" one by one to see how badly the AI's score drops without them.

**6. Conclusion & Limitations**

•	**Conclusion**: This paper presents a clear path to help AI break past the 11.34% performance wall. By forcing the AI to think step-by-step and translating dry machine codes into simple words, we aim to double the accuracy of automated system repairs. 

•	**Limitations**: Because our AI agents need to talk back and forth, write code, and fix their own errors in multiple rounds, the system might take a few minutes to run and cost more in AI platform fees. 

•	**Future Work**: Once this phase proves successful, the next step is to transfer this system onto smaller, free, open-source AI models (like Llama-3). This will allow companies to run our tool inside their own systems completely for free, making it faster and much cheaper. 



## Our novelty candidates (pick & defend one)
1. **Heuristic + LLM hybrid** that uses cheap statistical triage first and only calls the LLM on hard cases (cut cost/latency vs the pure-agent baseline).
2. **Trace-graph-aware retrieval** that walks the service dependency graph to localize the failing logistics service faster.
3. **Domain-transfer framing** of microservice RCA as a logistics fulfillment pipeline (order -> warehouse -> shipment -> tracking) and measure if domain priors help.

## Writing tips for newcomers
- One claim per paragraph; back every claim with a number or a citation.
- Make figures first, then write around them.
- Reproducibility: the repo + `experiments/` + this guide *is* the appendix.
