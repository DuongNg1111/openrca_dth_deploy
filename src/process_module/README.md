# PROCESS module — owner @HoangNguyen2803

**Job:** from `InputContext`, find the most likely root-cause component(s) and explain why.

**📋 Contract & Core API:**
```
analyze(ctx: InputContext, top_k: int = 1) -> list[RootCauseCandidate]
```

**📂 File Architecture**

- **transform.py** — Aggregates raw telemetry metrics into structured per-(component, KPI) time-series dataframes.

- **detect.py** — Anomaly detection and component ranking using advanced statistical methods (change-point z-score). The analytical heart of the pipeline.

- **reasoner.py** — Translates raw statistical anomalies into readable, human-understandable explanations and SRE insights (integrated with Gemini LLM).

**Beginner steps**
**🚀 Getting Started (Beginner Steps)**

         1/ Run python -m src.pipeline to execute the pipeline locally and confirm it properly targets order-service.
         
         
         2/ Inspect detect.py to understand the change-point z-score calculation algorithm.
         
         
         3/ M5 Milestone (Novelty): Enhance detection accuracy (advanced stats, log/trace signals, or LLM-driven reasoning). Important: Keep the analyze() contract strictly stable so DEV 1/3 integrations remain unbroken.

**🔄Execution Workflow**

Receive evidence

↓

Evaluate

↓

Complete ?

↓
   ├── Yes → Reasoner (Deep Root-Cause Analysis)
   
   └── No  → Return missing evidence report

**🎯 Job Responsibilities & Inputs/Outputs**

- Job: Validate evidence completeness rigorously before triggering root-cause analysis (RCA).

- Inputs:

      - Parsed Query
      
      - Investigation Metadata
      
      - Telemetry Metrics & Logs

- Output: ValidationResult (Proceed / Request Missing Evidence)
