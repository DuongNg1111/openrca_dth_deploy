from dataclasses import asdict
import json
import pandas as pd

from src.jira.receive_query import receive_query

# from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata

from src.process_module.preprocess import preprocess
from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import (
    build_investigation_context,
)

from src.process_module.service_selector import (
    select_services,
)

# Import Agents
from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent
from src.database.repository import get_investigation_evidence
from src.database.repository import (
    create_investigation,
    insert_metrics,
    insert_logs,
    insert_traces,
    save_rca_result,
    insert_evidence,
    get_investigation_evidence
)


def run_pipeline(issue_key, run_agents=False):

    # =====================================================
    # STEP 1
    # =====================================================

    print("\n========================================")
    print("STEP 1: RECEIVE USER QUERY")
    print("========================================")


    raw_query = receive_query(issue_key)

    ...


    print("\nRaw Query")

    raw_data = asdict(raw_query)

    for key, value in raw_data.items():

        if key == "additional_information":
            continue

        print(
            f"{key:<25}: {value}"
        )
    # =====================================================
    # STEP 2
    # =====================================================

    print("\n========================================")
    print("STEP 2: PARSE QUERY")
    print("========================================")

    parsed_query = parse_query(
        raw_query
    )

    print("\nParsed Information")

    print(
        "Keywords :",
        parsed_query.keywords,
    )

    print("\nInvestigation Window")

    print(
        "Start :",
        parsed_query.time_window.start,
    )

    print(
        "End   :",
        parsed_query.time_window.end,
    )

    # =====================================================
    # STEP 3
    # =====================================================

    print("\n========================================")
    print("STEP 3-4: LOAD TELEMETRY")
    print("========================================")

    from src.config import load_config
    config = load_config() # Gọi hàm load_config để lấy đúng data_root đã cấu hình trong config.py

    data_source = connect_data_source(
        parsed_query,
        config,
    )

    print("Data Source:", data_source)

    # =====================================================
    # STEP 5
    # =====================================================

    print("\n========================================")
    print("STEP 5: LOAD METADATA")
    print("========================================")

    metadata = load_metadata(
        data_source,
        parsed_query,
    )

    print("Date Folder :", metadata.date)
    print("Metric Files:", metadata.metric.count)
    print("Log Files   :", metadata.log.count)
    print("Trace Files :", metadata.trace.count)
    print("Total Files :", metadata.total_files)

    # =====================================================
    # STEP 6
    # =====================================================

    print("\n========================================")
    print("STEP 6: PREPROCESS")
    print("========================================")

    preprocessed = preprocess(
        metadata,
        parsed_query,
    )

    print("\nPreprocess Completed")

    # =====================================================
    # STEP 7
    # =====================================================

    print("\n========================================")
    print("STEP 7: BUILD READY-TO-CALL DATABASE")
    print("========================================")


    # =====================================================
    # STEP 7.1: BUILD SERVICE LINKS
    # =====================================================

    print("\n========================================")
    print("STEP 7.1: BUILD SERVICE LINKS")
    print("========================================")


    service_links = build_service_links(
        preprocessed
    )


    print(
        "Service Links Built:",
        len(service_links)
    )


    # =====================================================
    # STEP 7.2: PREPARE AGENT CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 7.2: PREPARE AGENT CONTEXT")
    print("========================================")


    print(
        "Ready-To-Call Context Prepared"
    )



    # =====================================================
    # STEP 7.3: SAVE INVESTIGATION
    # =====================================================

    print("\n========================================")
    print("STEP 7.3: SAVE INVESTIGATION")
    print("========================================")


    investigation_id = create_investigation(
        issue_key=parsed_query.issue_key,
        environment=parsed_query.environment,
        affected_system=parsed_query.affected_system,
        dataset=preprocessed.dataset,
        incident_time=parsed_query.incident_time,
        window_start=parsed_query.time_window.start,
        window_end=parsed_query.time_window.end,
        incident_description=raw_query.incident_description,
        reporter=raw_query.reporter,
        reporter_email="",
    )



    print(
        "Investigation ID:",
        investigation_id
    )



    # =====================================================
    # STEP 7.4: SAVE METRICS
    # =====================================================

    print("\n========================================")
    print("STEP 7.4: SAVE METRICS")
    print("========================================")


    for df in preprocessed.metrics.values():

        insert_metrics(
            investigation_id,
            df
        )


    print(
        "Metrics Saved"
    )



    # =====================================================
    # STEP 7.5: SAVE LOGS
    # =====================================================

    print("\n========================================")
    print("STEP 7.5: SAVE LOGS")
    # =====================================================


    for df in preprocessed.logs.values():

        insert_logs(
            investigation_id,
            df
        )


    print(
        "Logs Saved"
    )



    # =====================================================
    # STEP 7.6: SAVE TRACES
    # =====================================================

    print("\n========================================")
    print("STEP 7.6: SAVE TRACES")
    print("========================================")


    for df in preprocessed.traces.values():

        insert_traces(
            investigation_id,
            df
        )


    print(
        "Traces Saved"
    )

    # =====================================================
    # STEP 7.7: BUILD INVESTIGATION CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 7.7: BUILD INVESTIGATION CONTEXT")
    print("========================================")

    contexts = build_investigation_context(
        preprocessed,
        service_links,
        parsed_query,
        investigation_id=investigation_id,
    )

    print(
        "Contexts Built:",
        len(contexts)
    )
    # =====================================================
    # STEP 8
    # =====================================================

    print("\n========================================")
    print("STEP 8: SERVICE SELECTION")
    print("========================================")

    selected_contexts = select_services(
        parsed_query,
        contexts,
    )
    print("\n===== DEBUG SELECTED CONTEXTS =====")

    for key, context in selected_contexts.items():
        print(
            "KEY:",
            key,
            "| SERVICE:",
            context.service,
            "| INVESTIGATION:",
            context.investigation_id
        )

    print(
        "TOTAL SELECTED:",
        len(selected_contexts)
    )
    print("Affected System :", parsed_query.affected_system)
    print("Keywords        :", parsed_query.keywords)

    print("\nSelected Services :", len(selected_contexts))

    for service in selected_contexts.values():

        print("-", service.service)

    if not run_agents:

        print("\n========================================")
        print("PIPELINE STOPPED BEFORE AGENTS")
        print("READY FOR AGENT ANALYSIS")
        print("========================================")

        return selected_contexts

        # =====================================================
    # STEP 9: MULTI-AGENT ANALYSIS
    # =====================================================

    print("\n========================================")
    print("STEP 9: MULTI-AGENT ANALYSIS")
    print("========================================")

    metric_agent = MetricAgent()
    log_agent = LogAgent()
    trace_agent = TraceAgent()

    agent_results = {}

    print("Multi-agent analysis initialized.")
    print("Services to analyze:", len(selected_contexts))

    # =====================================================
    # STEP 10: METRIC AGENT
    # =====================================================

    print("\n========================================")
    print("STEP 10: METRIC AGENT")
    print("========================================")

    for context in selected_contexts.values():

        print("\n----------------------------------------")
        print("METRIC ANALYSIS")
        print("----------------------------------------")
        print("Investigation ID:", context.investigation_id)
        print("Service:", context.service)

print({
    "investigation_id": context.investigation_id,
    "service": context.service,
    "incident_time": context.incident_time
})

metric_result = metric_agent.analyze(context)

print("\nMETRIC RESULT")
print(
    json.dumps(
        metric_result,
        indent=2,
        default=str
    )
)

if context.service not in agent_results:
    agent_results[context.service] = {}

agent_results[context.service]["metric"] = metric_result


# =====================================================
# STEP 11: LOG AGENT
# =====================================================

print("\n========================================")
print("STEP 11: LOG AGENT")
print("========================================")

for context in selected_contexts.values():

    print("\n----------------------------------------")
    print("Log analysis")
    print("----------------------------------------")
    print("Investigation ID:", context.investigation_id)
    print("Service:", context.service)

    log_result = log_agent.analyze(context)

    print("\nLOG RESULT")
    print(
        json.dumps(
            log_result,
            indent=2,
            default=str
        )
    )

    agent_results[context.service]["log"] = log_result


# =====================================================
# STEP 12: TRACE AGENT
# =====================================================

print("\n========================================")
print("STEP 12: TRACE AGENT")
print("========================================")

for context in selected_contexts.values():

    print("\n----------------------------------------")
    print("Trace analysis")
    print("----------------------------------------")
    print("Investigation ID:", context.investigation_id)
    print("Service:", context.service)

    trace_result = trace_agent.analyze(context)

    print("\nTRACE RESULT")
    print(
        json.dumps(
            trace_result,
            indent=2,
            default=str
        )
    )

    agent_results[context.service]["trace"] = trace_result


# =====================================================
# STEP 13: EVIDENCE COLLECTION
# =====================================================

print("\n========================================")
print("STEP 13: EVIDENCE COLLECTION")
print("========================================")

for context in selected_contexts.values():

    results = agent_results[context.service]

    metric_result = results["metric"]
    log_result = results["log"]
    trace_result = results["trace"]

    print("\n----------------------------------------")
    print("Saving evidence")
    print("----------------------------------------")
    print("Service:", context.service)

    # ---------------------------------------------
    # SAVE METRIC EVIDENCE
    # ---------------------------------------------

    metric_anomalies = metric_result.get(
        "anomalies",
        []
    )

    for metric in metric_anomalies:

        insert_evidence(
            investigation_id=context.investigation_id,

            service=metric.get(
                "service",
                context.service
            ),

            evidence_type="metric",

            metric_name=metric.get(
                "metric"
            ),

            description=metric.get(
                "description",
                ""
            ),

            value=metric.get(
                "value"
            ),

            baseline=metric.get(
                "baseline"
            ),

            timestamp=metric.get(
                "timestamp"
            ),

            score=metric.get(
                "value"
            ),

            metadata=metric,

            confidence=metric_result.get(
                "confidence",
                0
            )
        )

    # ---------------------------------------------
    # SAVE LOG EVIDENCE
    # ---------------------------------------------

    log_entries = log_result.get(
        "logs",
        []
    )

    for log in log_entries:

        insert_evidence(
            investigation_id=context.investigation_id,

            service=log.get(
                "service",
                context.service
            ),

            evidence_type="log",

            description=log.get(
                "message",
                ""
            ),

            value=log.get(
                "count",
                0
            ),

            timestamp=log.get(
                "timestamp"
            ),

            score=float(
                log.get(
                    "count",
                    0
                )
            ),

            metadata=log,

            confidence=log_result.get(
                "confidence",
                0
            )
        )

    # ---------------------------------------------
    # SAVE TRACE EVIDENCE
    # ---------------------------------------------

    trace_entries = trace_result.get(
        "traces",
        []
    )

    for trace in trace_entries:

        insert_evidence(
            investigation_id=context.investigation_id,

            service=trace.get(
                "service",
                context.service
            ),

            evidence_type="trace",

            trace_id=trace.get(
                "trace_id"
            ),

            operation=trace.get(
                "operation"
            ),

            description=trace.get(
                "description",
                ""
            ),

            value=trace.get(
                "latency_ms",
                0
            ),

            baseline=trace.get(
                "baseline"
            ),

            timestamp=trace.get(
                "timestamp"
            ),

            score=trace.get(
                "latency_ms",
                0
            ),

            metadata=trace,

            confidence=trace_result.get(
                "confidence",
                0
            )
        )
    # =====================================================
    # STEP 14: EVIDENCE VALIDATION
    # =====================================================

    print("\n========================================")
    print("STEP 14: EVIDENCE VALIDATION")
    print("========================================")

    evidence_validation = {}

    for context in selected_contexts.values():

        evidence_df = get_investigation_evidence(
            context.investigation_id
        )

        count = (
            0
            if evidence_df is None
            else len(evidence_df)
        )

        evidence_validation[context.service] = {
            "valid": count > 0,
            "count": count
        }

        print(
            f"{context.service}: "
            f"{count} evidence records"
        )

    # =====================================================
    # STEP 15: EVIDENCE CORRELATION
    # =====================================================

    print("\n========================================")
    print("STEP 15: EVIDENCE CORRELATION")
    print("========================================")

    correlation_results = {}

    for context in selected_contexts.values():

        results = agent_results[context.service]

        metric_count = len(
            results["metric"].get(
                "anomalies",
                []
            )
        )

        log_count = len(
            results["log"].get(
                "logs",
                []
            )
        )

        trace_count = len(
            results["trace"].get(
                "traces",
                []
            )
        )

        correlation_results[context.service] = {
            "metric": metric_count,
            "log": log_count,
            "trace": trace_count,
            "total": (
                metric_count
                + log_count
                + trace_count
            )
        }

        print(
            f"{context.service}: "
            f"metric={metric_count}, "
            f"log={log_count}, "
            f"trace={trace_count}"
        )

    # =====================================================
    # STEP 16: FAULT LOCALIZATION
    # =====================================================

    print("\n========================================")
    print("STEP 16: FAULT LOCALIZATION")
    print("========================================")

    fault_candidates = {}

    for context in selected_contexts.values():

        correlation = correlation_results[
            context.service
        ]

        evidence_types = []

        if correlation["metric"] > 0:
            evidence_types.append("metric")

        if correlation["log"] > 0:
            evidence_types.append("log")

        if correlation["trace"] > 0:
            evidence_types.append("trace")

        fault_candidates[context.service] = {
            "service": context.service,
            "evidence_types": evidence_types,
            "evidence_count": correlation["total"]
        }

        print(
            f"{context.service}: "
            f"{evidence_types}"
        )

    # =====================================================
    # STEP 17: PREPARE REASONING CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 17: PREPARE REASONING CONTEXT")
    print("========================================")

    reasoning_contexts = {}

    for context in selected_contexts.values():

        evidence_df = get_investigation_evidence(
            context.investigation_id
        )

        reasoning_contexts[context.service] = {
            "context": context,
            "evidence": evidence_df,
            "agent_results": agent_results[
                context.service
            ],
            "fault_candidate": fault_candidates[
                context.service
            ]
        }

        print(
            f"Reasoning context ready: "
            f"{context.service}"
        )

    # =====================================================
    # STEP 18: REASONING AGENT
    # =====================================================

    print("\n========================================")
    print("STEP 18: REASONING AGENT")
    print("========================================")

    reasoning_agent = ReasoningAgent()

    rca_results = []

    for service, reasoning_data in reasoning_contexts.items():

        context = reasoning_data["context"]
        evidence_df = reasoning_data["evidence"]

        print("\n----------------------------------------")
        print("REASONING CONTEXT")
        print("----------------------------------------")

        print({
            "investigation_id": context.investigation_id,
            "service": context.service,
            "incident_time": context.incident_time
        })

        final_result = reasoning_agent.analyze(
            context,
            evidence_df
        )

        print("\n========== REASONING RESULT ==========")

        print(json.dumps(
            final_result,
            indent=2,
            default=str
        ))

        # =================================================
        # STEP 19: PROCESS RCA RESULT
        # =================================================

        print("\n========================================")
        print("STEP 19: PROCESS RCA RESULT")
        print("========================================")

        root_cause = final_result.get(
            "root_cause",
            final_result.get(
                "reason",
                ""
            )
        )

        confidence = final_result.get(
            "confidence",
            0
        )

        explanation = final_result.get(
            "explanation",
            final_result.get(
                "reasoning",
                ""
            )
        )

        try:
            confidence = float(confidence)
        except (
            TypeError,
            ValueError
        ):
            confidence = 0.0

        if root_cause is None:
            root_cause = ""

        if explanation is None:
            explanation = ""

        print("Service    :", context.service)
        print("Root Cause :", root_cause)
        print("Confidence :", confidence)
        print("Explanation:", explanation)

        # =================================================
        # STEP 20: SAVE RCA RESULT
        # =================================================

        print("\n========================================")
        print("STEP 20: SAVE RCA RESULT")
        print("========================================")

        save_rca_result(
            investigation_id=context.investigation_id,
            root_cause=root_cause,
            confidence=confidence,
            explanation=explanation
        )

        print(
            f"RCA saved successfully for "
            f"{context.service}"
        )

        rca_results.append({
            "investigation_id":
                context.investigation_id,
            "service":
                context.service,
            "root_cause":
                root_cause,
            "confidence":
                confidence,
            "explanation":
                explanation
        })

    # =====================================================
    # STEP 21: OUTPUT
    # =====================================================

    print("\n========================================")
    print("STEP 21: OUTPUT")
    print("========================================")

    print(
        "RCA results generated:",
        len(rca_results)
    )

    print("\nFINAL RCA OUTPUT")

    print(json.dumps(
        rca_results,
        indent=2,
        default=str
    ))

    # =====================================================
    # STEP 22: INTEGRATION & DEMO
    # =====================================================

    print("\n========================================")
    print("STEP 22: INTEGRATION & DEMO")
    print("========================================")

    print("Input      : Jira Issue")
    print("Telemetry  : Metrics / Logs / Traces")
    print("Agents     : Metric / Log / Trace")
    print("Reasoning  : ReasoningAgent")
    print("Database   : PostgreSQL")
    print("Output     : RCA Result")

    for result in rca_results:

        print(
            f"- {result['service']}: "
            f"{result['root_cause']} "
            f"(confidence={result['confidence']})"
        )

    # =====================================================
    # PIPELINE COMPLETED
    # =====================================================

    print("\n========================================")
    print("STEP 1-22 COMPLETED")
    print("========================================")

    print(json.dumps(
        rca_results,
        indent=2,
        default=str
    ))


    reasoning_agent = ReasoningAgent()

    rca_results = []

    for service, reasoning_data in reasoning_contexts.items():

        context = reasoning_data["context"]
        evidence_df = reasoning_data["evidence"]

        print("\n----------------------------------------")
        print("REASONING CONTEXT")
        print("----------------------------------------")

        print(
            {
                "investigation_id": context.investigation_id,
                "service": context.service,
                "incident_time": context.incident_time
            }
        )

        evidence_count = (
            0
            if evidence_df is None
            else len(evidence_df)
        )

        print(
            "Evidence rows:",
            evidence_count
        )

        # ---------------------------------------------
        # RUN REASONING AGENT
        # ---------------------------------------------

        final_result = reasoning_agent.analyze(
            context,
            evidence_df
        )

        print("\n========== REASONING RESULT ==========")

        print(
            json.dumps(
                final_result,
                indent=2,
                default=str
            )
        )

        # =================================================
        # STEP 19: PROCESS RCA RESULT
        # =================================================

        print("\n========================================")
        print("STEP 19: PROCESS RCA RESULT")
        print("========================================")

        root_cause = final_result.get(
            "root_cause",
            final_result.get(
                "reason",
                ""
            )
        )

        confidence = final_result.get(
            "confidence",
            0
        )

        explanation = final_result.get(
            "explanation",
            final_result.get(
                "reasoning",
                ""
            )
        )

        try:
            confidence = float(
                confidence
            )
        except (
            TypeError,
            ValueError
        ):
            confidence = 0.0

        if root_cause is None:
            root_cause = ""

        if explanation is None:
            explanation = ""

        print(
            "Service    :",
            context.service
        )

        print(
            "Root Cause :",
            root_cause
        )

        print(
            "Confidence :",
            confidence
        )

        print(
            "Explanation:",
            explanation
        )

        processed_result = {
            "investigation_id": context.investigation_id,
            "service": context.service,
            "root_cause": root_cause,
            "confidence": confidence,
            "explanation": explanation
        }

        # =================================================
        # STEP 20: SAVE RCA RESULT
        # =================================================

        print("\n========================================")
        print("STEP 20: SAVE RCA RESULT")
        print("========================================")

        save_rca_result(
            investigation_id=context.investigation_id,

            root_cause=root_cause,

            confidence=confidence,

            explanation=explanation
        )

        print(
            "RCA saved successfully."
        )

        rca_results.append(
            processed_result
        )

    # =====================================================
    # STEP 21: OUTPUT
    # =====================================================

    print("\n========================================")
    print("STEP 21: OUTPUT")
    print("========================================")

    print(
        "RCA results generated:",
        len(rca_results)
    )

    print("\nFINAL RCA OUTPUT")

    print(
        json.dumps(
            rca_results,
            indent=2,
            default=str
        )
    )

    # =====================================================
    # STEP 22: INTEGRATION & DEMO
    # =====================================================

    print("\n========================================")
    print("STEP 22: INTEGRATION & DEMO")
    print("========================================")

    print("Pipeline integration completed.")
    print("Input        : Jira Issue")
    print("Telemetry    : Metrics / Logs / Traces")
    print("Processing   : Multi-Agent RCA")
    print("Reasoning    : ReasoningAgent")
    print("Database     : PostgreSQL")
    print("Output       : RCA Result")

    print("\nServices processed:")

    for result in rca_results:

        print(
            f"- {result['service']}: "
            f"{result['root_cause']} "
            f"(confidence={result['confidence']})"
        )

    # =====================================================
    # PIPELINE COMPLETED
    # =====================================================

    print("\n========================================")
    print("STEP 1-22 COMPLETED")
    print("========================================")

    print(
        json.dumps(
            rca_results,
            indent=2,
            default=str
        )
    )

    return rca_results
if __name__ == "__main__":

    issue_key = input(
        "Enter Jira Issue Key: "
    )

    run_pipeline(
        issue_key,
        run_agents=True
    )