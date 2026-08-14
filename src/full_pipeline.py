import argparse
import json
from pathlib import Path
from dataclasses import asdict

import pandas as pd

from src.config import load_config
from src.schemas import RawQuery

from src.database.repository import (
    create_investigation,
    update_investigation_status,
    get_investigation_evidence,
    insert_evidence,
    insert_logs,
    insert_metrics,
    insert_traces,
    save_rca_result,
)

from src.input_module.metadata_loader import load_metadata
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.jira.receive_query import receive_query

from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent
from src.process_module.agents.trace_agent import TraceAgent

from src.process_module.evidence_builder import (
    build_investigation_context,
)

from src.process_module.evidence_checker import validate
from src.process_module.link_telemetry import build_service_links
from src.process_module.preprocess import preprocess
from src.process_module.service_selector import select_services

# Import Agents
from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent
from src.database.repository import (
    create_investigation,
    insert_metrics,
    insert_logs,
    insert_traces,
    save_rca_result,
    insert_evidence
)

FULL_PIPELINE_REQUIRED_MODALITIES = (
    "metric",
    "log",
    "trace",
)

class EvidenceValidationError(RuntimeError):
    """
    Raised when prepared telemetry is incomplete
    after confirming that telemetry data exists.
    """


def _require_prepared_evidence(
    parsed_query,
    preprocessed,
    metadata,
):
    validation = validate(
        parsed_query,
        preprocessed,
        metadata,
        required_modalities=FULL_PIPELINE_REQUIRED_MODALITIES,
    )

    if validation.ready_for_reasoning:
        return validation

    missing = (
        ", ".join(validation.missing_evidence)
        or "unknown evidence"
    )

    actions = " ".join(
        validation.next_actions
    )

    raise EvidenceValidationError(
        "Evidence validation failed before database writes. "
        f"Missing: {missing}. {actions}"
    )


def _load_raw_query_file(
    path: str | Path,
) -> RawQuery:

    payload = json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "Raw query JSON must contain an object"
        )

    return RawQuery(**payload)


def _has_telemetry_data(
    preprocessed,
):
    """
    Check whether the investigation window
    contains at least one telemetry record
    across metric, log, or trace data.
    """

    for telemetry_group in (
        preprocessed.metrics,
        preprocessed.logs,
        preprocessed.traces,
    ):

        for df in telemetry_group.values():

            if (
                df is not None
                and not df.empty
            ):
                return True

    return False


def run_pipeline(
    issue_key=None,
    run_agents=False,
    *,
    dry_run=True,
    raw_query=None,
    config=None,
):
    """
    Prepare or execute the full pipeline.

    The Python API is non-writing by default.
    Database persistence requires:
        dry_run=False

    Agent execution additionally requires:
        run_agents=True
    """

    if type(dry_run) is not bool:
        raise TypeError(
            "dry_run must be an actual bool; "
            "only exact False permits writes"
        )

    if type(run_agents) is not bool:
        raise TypeError(
            "run_agents must be an actual bool; "
            "only exact True permits agents"
        )

    if dry_run and run_agents:
        raise ValueError(
            "dry_run cannot be combined with run_agents"
        )

    # =====================================================
    # STEP 1
    # =====================================================

    print("\n========================================")
    print("STEP 1: RECEIVE USER QUERY")
    print("========================================")

    if raw_query is None:

        if not issue_key:
            raise ValueError(
                "issue_key or raw_query is required"
            )

        raw_query = receive_query(
            issue_key
        )

    print("\nRaw Query")

    raw_data = asdict(
        raw_query
    )

    for key, value in raw_data.items():

        if key in {
            "additional_information",
            "reporter_email",
        }:
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
    # STEP 3-4
    # =====================================================

    print("\n========================================")
    print("STEP 3-4: LOAD TELEMETRY")
    print("========================================")

    if config is None:
        config = load_config()

    data_source = connect_data_source(
        parsed_query,
        config,
    )

    print(
        "Data Source:",
        data_source,
    )

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

    print(
        "Date Folder :",
        metadata.date,
    )

    print(
        "Metric Files:",
        metadata.metric.count,
    )

    print(
        "Log Files   :",
        metadata.log.count,
    )

    print(
        "Trace Files :",
        metadata.trace.count,
    )

    print(
        "Total Files :",
        metadata.total_files,
    )

    # =====================================================
    # STEP 6
    # =====================================================

    print("\n========================================")
    print("STEP 6: PREPROCESS")
    print("========================================")

    preprocessed = preprocess(
        metadata,
        parsed_query,
        timestamp_offset_hours=config.get(
            "timestamp_offset_hours",
            0,
        ),
    )

    print(
        "\nPreprocess Completed"
    )

    # =====================================================
    # STEP 7
    # =====================================================

    print("\n========================================")
    print("STEP 7: BUILD READY-TO-CALL DATABASE")
    print("========================================")

    # =====================================================
    # STEP 7.1: CREATE INVESTIGATION
    # =====================================================

    print("\n========================================")
    print("STEP 7.1: SAVE INVESTIGATION")
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
        reporter_email=raw_query.reporter_email,
    )

    print(
        "Investigation ID:",
        investigation_id,
    )

    update_investigation_status(
        investigation_id,
        "Processing",
    )

    print(
        "Investigation Status: Processing"
    )

    # =====================================================
    # STEP 7.2: CHECK TELEMETRY DATA
    # =====================================================

    print("\n========================================")
    print("CHECK TELEMETRY DATA")
    print("========================================")

    if not _has_telemetry_data(
        preprocessed
    ):

        print(
            "\nNO DATA FOUND"
        )

        update_investigation_status(
            investigation_id,
            "No Data",
        )

        print(
            "Investigation Status: No Data"
        )

        return {
            "issue_key": parsed_query.issue_key,
            "status": "No Data",
            "message": "No telemetry data found.",
            "investigation_id": investigation_id,
        }

    print(
        "Telemetry data found. "
        "Continuing pipeline..."
    )

    # =====================================================
    # STEP 7.3: EVIDENCE VALIDATION
    # =====================================================

    print("\n========================================")
    print("STEP 7.3: EVIDENCE VALIDATION")
    print("========================================")

    preparation_validation = (
        _require_prepared_evidence(
            parsed_query,
            preprocessed,
            metadata,
        )
    )

    print(
        "Evidence validation:",
        preparation_validation.status,
        f"(confidence={preparation_validation.confidence:.2f})",
    )

    # =====================================================
    # STEP 7.4: BUILD SERVICE LINKS
    # =====================================================

    print("\n========================================")
    print("STEP 7.4: BUILD SERVICE LINKS")
    print("========================================")

    service_links = build_service_links(
        preprocessed
    )

    print(
        "Service Links Built:",
        len(service_links),
    )

    if not service_links:

        raise EvidenceValidationError(
            "Evidence validation failed before "
            "database writes. "
            "No logical service could be mapped "
            "from telemetry cmdb_id values."
        )

    # =====================================================
    # DRY RUN
    # =====================================================

    if dry_run:

        print("\n========================================")
        print(
            "DRY RUN COMPLETE — "
            "NO DATABASE WRITES"
        )
        print("========================================")

        return {
            "raw_query": raw_query,
            "parsed_query": parsed_query,
            "metadata": metadata,
            "preprocessed": preprocessed,
            "evidence_validation":
                preparation_validation,
            "service_links":
                service_links,
        }

    # =====================================================
    # STEP 7.5: PREPARE AGENT CONTEXT
    # =====================================================

    print("\n========================================")
    print("STEP 7.5: PREPARE AGENT CONTEXT")
    print("========================================")

    print(
        "Ready-To-Call Context Prepared"
    )

    # =====================================================
    # STEP 7.6: SAVE METRICS
    # =====================================================

    print("\n========================================")
    print("STEP 7.6: SAVE METRICS")
    print("========================================")

    for df in preprocessed.metrics.values():

        insert_metrics(
            investigation_id,
            df,
        )

    print(
        "Metrics Saved"
    )

    # =====================================================
    # STEP 7.7: SAVE LOGS
    # =====================================================

    print("\n========================================")
    print("STEP 7.7: SAVE LOGS")
    print("========================================")

    for df in preprocessed.logs.values():

        insert_logs(
            investigation_id,
            df,
        )

    print(
        "Logs Saved"
    )

    # =====================================================
    # STEP 7.8: SAVE TRACES
    # =====================================================

    print("\n========================================")
    print("STEP 7.8: SAVE TRACES")
    print("========================================")

    for df in preprocessed.traces.values():

        insert_traces(
            investigation_id,
            df,
        )

    print(
        "Traces Saved"
    )

    # =====================================================
    # STEP 7.9: BUILD INVESTIGATION CONTEXT
    # =====================================================

    print("\n========================================")
    print(
        "STEP 7.9: BUILD INVESTIGATION CONTEXT"
    )
    print("========================================")

    contexts = build_investigation_context(
        preprocessed,
        service_links,
        parsed_query,
        investigation_id=investigation_id,
    )

    print(
        "Contexts Built:",
        len(contexts),
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

    print(
        "Affected System :",
        parsed_query.affected_system,
    )

    print(
        "Keywords        :",
        parsed_query.keywords,
    )

    print(
        "\nSelected Services :",
        len(selected_contexts),
    )

    for service in selected_contexts.values():

        print(
            "-",
            service.service,
        )

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

    metric_agent = MetricAgent(
        config=config
    )

    log_agent = LogAgent(
        config=config
    )

    trace_agent = TraceAgent(
        config=config
    )

    reasoning_agent = ReasoningAgent(
        config=config
    )

    agent_results = {}


    for context in selected_contexts.values():
        print("\n----------------------------------------")
        print("SERVICE :", context.service)
        print("----------------------------------------")

        metric_result = metric_agent.analyze(context)
        log_result = log_agent.analyze(context)
        trace_result = trace_agent.analyze(context)

        # Chỉ gọi 1 lần với đầy đủ context và kết quả 3 agent
        final_output = reasoning_agent.analyze(
            context,
            metric_result,
            log_result,
            trace_result
        )

        # 1. Lưu kết quả nguyên nhân gốc rễ (RCA) vào bảng rca_results
        save_rca_result(
            investigation_id= investigation_id,
            root_cause=final_output.get("reason", "unknown"),
            confidence=float(final_output.get("confidence", 0.0)),
            explanation=final_output.get("reasoning", "")
        )

        # 2. Lưu kết quả bằng chứng Metric vào bảng evidence_records
        for metric in final_output.get("metrics", []):
            insert_evidence(
                investigation_id= investigation_id,
                service=context.service,
                evidence_type="metric",
                description=metric.get("description",""),
                score=float(metric.get("value", 0.0))
            )
        # 3. Lưu kết quả bằng chứng Log vào bảng evidence_records
        for log in final_output.get("logs", []):
            insert_evidence(
                investigation_id= investigation_id,
                service=context.service,
                evidence_type="log",
                description=log.get("message",""),
                score=float(log.get("count", 1.0))
            )
        # 4. Lưu kết quả bằng chứng Trace vào bảng evidence_records
        for trace in final_output.get("traces", []):
            insert_evidence(
                investigation_id= investigation_id,
                service=context.service,
                evidence_type="trace",
                description=trace.get("description",""),
                score=float(trace.get("latency_ms", 0.0))
            )
        print("\nFinal Output JSON format:")
        print(json.dumps(final_output, indent=4, default=str))


    # =====================================================
    # STEP 10: METRIC AGENT
    # =====================================================

    print("\n========================================")
    print("STEP 10: METRIC AGENT")
    print("========================================")
    agent_results = {}

    # Sắp xếp và chỉ chọn ra Top các dịch vụ có dấu hiệu bất thường cao nhất (Outliers)
    sorted_contexts = sorted(
        selected_contexts.values(),
        key=lambda c: getattr(c, 'anomaly_score', 0),
        reverse=True
    )

    TOP_N = 3
    target_contexts = sorted_contexts[:TOP_N] if len(sorted_contexts) > TOP_N else sorted_contexts

    print(f"Tổng số dịch vụ ban đầu: {len(selected_contexts)}")
    print(f"Đã chọn ra {len(target_contexts)} dịch vụ trọng điểm để phân tích.")

    for context in target_contexts:
        print("\n----------------------------------------")
        print(f"METRIC ANALYSIS FOR: {context.service}")
        print("----------------------------------------")

        print(
            {
                "investigation_id": context.investigation_id,
                "service": context.service,
                "incident_time": context.incident_time,
            }
        )

        try:
            metric_result = metric_agent.analyze(context)
            print("\nMETRIC RESULT")
            print(json.dumps(metric_result, indent=2, default=str))

            agent_results[context.service] = {
                "metric": metric_result
            }
        except Exception as e:
            print(f"Lỗi metric service {context.service}: {str(e)}")
            agent_results[context.service] = {
                "metric": {"error": str(e), "anomalies": []}
            }

    # =====================================================
    # STEP 11: LOG AGENT
    # =====================================================

    print("\n========================================")
    print("STEP 11: LOG AGENT")
    print("========================================")

    for context in target_contexts:

        print("\n----------------------------------------")
        print(f"LOG ANALYSIS FOR: {context.service}")
        print("----------------------------------------")

        try:
            log_result = log_agent.analyze(context)
            print("\nLOG RESULT")
            print(json.dumps
                (
                log_result,
                indent=2,
                default=str
                )
                )
            # Đảm bảo key metric đã tồn tại trước khi gán thêm log
            if context.service not in agent_results:
                agent_results[context.service] = {}

            agent_results[
                context.service
            ]["log"] = log_result
        except Exception as e:
            print(f"Lỗi log service {context.service}: {str(e)}")
            agent_results[context.service]["log"] = {"error": str(e), "logs": []}

    # =====================================================
    # STEP 12: TRACE AGENT
    # =====================================================

    print("\n========================================")
    print("STEP 12: TRACE AGENT")
    print("========================================")

    for context in target_contexts:

        print("\n----------------------------------------")
        print(f"TRACE ANALYSIS FOR: {context.service}")
        print("----------------------------------------")
        try:
            trace_result = trace_agent.analyze(
                context
            )

            print("\nTRACE RESULT")

            print(
                json.dumps(
                    trace_result,
                    indent=2,
                    default=str,
                )
            )

            agent_results[
                context.service
            ]["trace"] = trace_result
        except Exception as e:
            print(f"Lỗi trace service {context.service}: {str(e)}")
            agent_results[context.service]["trace"] = {"error": str(e), "traces": []}

    # =====================================================
    # STEP 13: EVIDENCE COLLECTION
    # =====================================================

    print("\n========================================")
    print("STEP 13: EVIDENCE COLLECTION")
    print("========================================")

    for context in target_contexts:

        results = agent_results.get(
            context.service,
            {}
        )

        metric_result = results.get("metric", {})
        log_result = results.get("log", {})
        trace_result = results.get("trace", {})

        metric_anomalies = metric_result.get(
            "anomalies",
            [],
        )

        log_entries = log_result.get(
            "logs",
            [],
        )

        trace_entries = trace_result.get(
            "traces",
            [],
        )

        # -------------------------------------------------
        # METRIC EVIDENCE
        # -------------------------------------------------

        for metric in metric_anomalies:

            insert_evidence(
                investigation_id=context.investigation_id,
                service=metric.get(
                    "service",
                    context.service,
                ),
                evidence_type="metric",
                metric_name=metric.get(
                    "metric"
                ),
                description=metric.get(
                    "description"
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
                    0,
                ),
            )

        # -------------------------------------------------
        # LOG EVIDENCE
        # -------------------------------------------------

        for log in log_entries:

            insert_evidence(
                investigation_id=context.investigation_id,
                service=log.get(
                    "service",
                    context.service,
                ),
                evidence_type="log",
                description=log.get(
                    "message",
                    "",
                ),
                score=float(
                    log.get(
                        "count",
                        0,
                    )
                ),
                timestamp=log.get(
                    "timestamp"
                ),
                value=float(
                    log.get(
                        "count",
                        0,
                    )
                ),
                metadata=log,
                confidence=log_result.get(
                    "confidence",
                    0,
                ),
            )

        # -------------------------------------------------
        # TRACE EVIDENCE
        # -------------------------------------------------

        for trace in trace_entries:

            insert_evidence(
                investigation_id=context.investigation_id,
                service=trace.get(
                    "service",
                    context.service,
                ),
                evidence_type="trace",
                trace_id=trace.get(
                    "trace_id"
                ),
                operation=trace.get(
                    "operation"
                ),
                description=trace.get(
                    "description"
                ),
                value=trace.get(
                    "latency_ms"
                ),
                baseline=trace.get(
                    "baseline_ms"
                ),
                score=trace.get(
                    "latency_ms"
                ),
                metadata=trace,
                confidence=trace_result.get(
                    "confidence",
                    0,
                ),
            )

        print(
            f"{context.service}: "
            f"metrics={len(metric_anomalies)}, "
            f"logs={len(log_entries)}, "
            f"traces={len(trace_entries)}"
        )


    # =====================================================
    # STEP 14: EVIDENCE VALIDATION
    # =====================================================

    print("\n========================================")
    print("STEP 14: EVIDENCE VALIDATION")
    print("========================================")

    evidence_validation = {}

    for context in target_contexts:

        evidence_df = get_investigation_evidence(
            context.investigation_id
        )

        count = (
            0
            if evidence_df is None
            else len(evidence_df)
        )

        evidence_validation[
            context.service
        ] = {
            "valid": count > 0,
            "count": count,
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

    for context in target_contexts:

        results = agent_results.get(context.service, {})

        metric_count = len(
            results.get("metric", {}).get(
                "anomalies",
                []
            )
        )

        log_count = len(
            results.get("log", {}).get("logs", [])
        )

        trace_count = len(
            results.get("trace", {}).get("traces", [])
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

    for context in target_contexts:
        # Dùng .get() để tránh lỗi nếu key không tồn tại
        correlation = correlation_results.get(
            context.service,
            {"metric": 0, "log": 0, "trace": 0, "total": 0}
        )

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
    # =====================================================

    reasoning_contexts = {}

    for context in target_contexts:

        evidence_df = get_investigation_evidence(
            context.investigation_id
        )

        reasoning_contexts[context.service] = {
            "context": context,
            "evidence": evidence_df,
            "agent_results": agent_results.get(
                context.service, {}
            ),
            "fault_candidate": fault_candidates.get(
                context.service, {}
            )
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

    reasoning_agent = ReasoningAgent(config=config)

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
            "incident_time": context.incident_time,
        })

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
            service=context.service,
            root_cause=root_cause,
            confidence=confidence,
            explanation=explanation,
        )

        print(
            f"RCA saved successfully for "
            f"{context.service}"
        )

        rca_results.append({
            "investigation_id": context.investigation_id,
            "service": context.service,
            "root_cause": root_cause,
            "confidence": confidence,
            "explanation": explanation,
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

    print(
        json.dumps(
            rca_results,
            indent=2,
            default=str
        )
    )

    # Only mark Completed when RCA results actually exist.
    if rca_results:

        update_investigation_status(
            investigation_id,
            "Completed"
        )

        print(
            "Investigation Status: Completed"
        )

    else:

        update_investigation_status(
            investigation_id,
            "No Data"
        )

        print(
            "Investigation Status: No Data"
        )


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

    print(
        json.dumps(
            rca_results,
            indent=2,
            default=str
        )
    )

    return rca_results


    # =====================================================
    # COMMAND LINE INTERFACE
    # =====================================================

    def main(argv=None):

        parser = argparse.ArgumentParser(
            description="Run the OpenRCA full pipeline"
        )

        source = parser.add_mutually_exclusive_group(
            required=True
        )

        source.add_argument(
            "--issue",
            help="Read a Jira issue by key"
        )

        source.add_argument(
            "--raw-query-file",
            type=Path,
            help="Read a local RawQuery JSON file instead of contacting Jira"
        )

        parser.add_argument(
            "--config",
            type=Path,
            help="Path to a YAML configuration file"
        )

        parser.add_argument(
            "--data-root",
            type=Path,
            help="Override the local Market data root"
        )

        parser.add_argument(
            "--dataset",
            help="Override the dataset name"
        )

        parser.add_argument(
            "--timestamp-offset-hours",
            type=float,
            help="Convert numeric UTC telemetry timestamps into incident-local time"
        )

        parser.add_argument(
            "--write-database",
            action="store_true",
            help="Allow PostgreSQL writes; omitted by default for safety"
        )

        parser.add_argument(
            "--run-agents",
            action="store_true",
            help="Run Gemini-backed agents after database persistence"
        )

        args = parser.parse_args(argv)

        if args.run_agents and not args.write_database:

            parser.error(
                "--run-agents requires --write-database"
            )

        local_query = (
            _load_raw_query_file(args.raw_query_file)
            if args.raw_query_file is not None
            else None
        )

        runtime_config = load_config(
            args.config
        )

        if args.data_root is not None:
            runtime_config["data_root"] = str(
                args.data_root
            )

        if args.dataset is not None:
            runtime_config["dataset_override"] = args.dataset

        if args.timestamp_offset_hours is not None:
            runtime_config["timestamp_offset_hours"] = (
                args.timestamp_offset_hours
            )

        result = run_pipeline(
            args.issue,
            run_agents=args.run_agents,
            dry_run=not args.write_database,
            raw_query=local_query,
            config=runtime_config,
        )

        if not args.write_database:

            validation = result["evidence_validation"]

            print(
                json.dumps(
                    {
                        "status": validation.status,
                        "confidence": validation.confidence,
                        "dataset": result["preprocessed"].dataset,
                        "services": sorted(
                            result["service_links"]
                        ),
                        "database_writes": False,
                    },
                    indent=2,
                )
            )


    if __name__ == "__main__":
        main()