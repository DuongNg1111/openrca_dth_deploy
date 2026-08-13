from __future__ import annotations

from dataclasses import dataclass, field


# ==========================================================
# CONFIGURATION
# ==========================================================

MAX_RETRY = 3

CONFIDENCE_THRESHOLD = 0.80

MIN_CHECK_SCORE = 5

TOTAL_CHECKS = 6

# Metric is abnormal when:
# |value - baseline| / |baseline| >= 20%
METRIC_DEVIATION_THRESHOLD = 0.20

# Trace is abnormal when:
# latency / baseline >= 1.5x
LATENCY_RATIO_THRESHOLD = 1.5


# ==========================================================
# CHECKLIST RESULT
# ==========================================================

@dataclass
class ChecklistResult:
    status: str
    score: int
    max_score: int
    retry_required: bool

    failed_checks: list[str] = field(
        default_factory=list
    )

    recommendation: str = ""

    check_results: dict[str, bool] = field(
        default_factory=dict
    )

    check_details: dict[str, str] = field(
        default_factory=dict
    )


# ==========================================================
# HELPERS
# ==========================================================

def _get_evidence(candidate):
    evidence = getattr(
        candidate,
        "evidence",
        None
    )

    if not isinstance(evidence, dict):
        return {}

    return evidence


def _to_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ==========================================================
# 1. METRIC AGENT CHECK
# ==========================================================

def check_metric(candidate) -> bool:
    """
    Validate whether Metric Agent identified
    a real abnormal metric by comparing value
    against baseline.
    """

    evidence = _get_evidence(candidate)

    metrics = evidence.get(
        "metrics",
        []
    )

    if not metrics:
        return False

    for metric in metrics:

        if not isinstance(metric, dict):
            continue

        value = _to_float(
            metric.get("value")
        )

        baseline = _to_float(
            metric.get("baseline")
        )

        severity = str(
            metric.get(
                "severity",
                metric.get(
                    "status",
                    ""
                )
            )
        ).lower()

        # Explicit severe anomaly
        if severity in [
            "error",
            "critical",
        ]:
            return True

        # Baseline comparison
        if (
            value is None
            or baseline is None
            or baseline == 0
        ):
            continue

        deviation = (
            abs(value - baseline)
            / abs(baseline)
        )

        if deviation >= METRIC_DEVIATION_THRESHOLD:
            return True

    return False


def get_metric_detail(candidate) -> str:

    evidence = _get_evidence(candidate)

    metrics = evidence.get(
        "metrics",
        []
    )

    if not metrics:
        return (
            "Metric Agent returned no metric evidence."
        )

    for metric in metrics:

        if not isinstance(metric, dict):
            continue

        name = str(
            metric.get(
                "metric",
                metric.get(
                    "name",
                    "Metric"
                )
            )
        )

        value = _to_float(
            metric.get("value")
        )

        baseline = _to_float(
            metric.get("baseline")
        )

        if (
            value is not None
            and baseline is not None
            and baseline != 0
        ):

            deviation = (
                abs(value - baseline)
                / abs(baseline)
                * 100
            )

            if deviation >= (
                METRIC_DEVIATION_THRESHOLD * 100
            ):
                return (
                    f"{name}: value={value:.3f}, "
                    f"baseline={baseline:.3f}, "
                    f"deviation={deviation:.1f}%. "
                    "Metric anomaly confirmed."
                )

    return (
        "Metric Agent returned metrics, "
        "but no significant deviation from "
        "baseline was detected."
    )


# ==========================================================
# 2. LOG AGENT CHECK
# ==========================================================

def check_log(candidate) -> bool:
    """
    Validate Log Agent output.

    Empty logs are NOT automatically considered
    a failure.

    If logs exist, at least one must contain
    an actual error/warning signal.
    """

    evidence = _get_evidence(candidate)

    logs = evidence.get(
        "logs",
        []
    )

    # No logs can be a valid result:
    # Log Agent found no explicit error.
    if not logs:
        return True

    error_keywords = [
        "error",
        "exception",
        "failed",
        "failure",
        "fail",
        "timeout",
        "critical",
        "panic",
        "unavailable",
        "refused",
    ]

    for log in logs:

        if not isinstance(log, dict):
            continue

        level = str(
            log.get(
                "level",
                log.get(
                    "severity",
                    ""
                )
            )
        ).lower()

        message = str(
            log.get(
                "message",
                log.get(
                    "description",
                    ""
                )
            )
        ).lower()

        if level in [
            "error",
            "fatal",
            "critical",
            "warn",
            "warning",
        ]:
            return True

        if any(
            keyword in message
            for keyword in error_keywords
        ):
            return True

    return False


def get_log_detail(candidate) -> str:

    evidence = _get_evidence(candidate)

    logs = evidence.get(
        "logs",
        []
    )

    if not logs:
        return (
            "Log Agent found no explicit "
            "error/warning log evidence."
        )

    for log in logs:

        if not isinstance(log, dict):
            continue

        level = str(
            log.get(
                "level",
                log.get(
                    "severity",
                    ""
                )
            )
        ).lower()

        message = str(
            log.get(
                "message",
                log.get(
                    "description",
                    ""
                )
            )
        ).lower()

        if level in [
            "error",
            "fatal",
            "critical",
            "warn",
            "warning",
        ]:
            return (
                f"Log Agent detected "
                f"{level} level evidence."
            )

        if any(
            keyword in message
            for keyword in [
                "error",
                "exception",
                "failed",
                "failure",
                "timeout",
                "critical",
                "panic",
            ]
        ):
            return (
                "Log Agent detected an "
                "error-related message."
            )

    return (
        "Logs were returned, but no "
        "error/warning signal was detected."
    )


# ==========================================================
# 3. TRACE AGENT CHECK
# ==========================================================

def check_trace(candidate) -> bool:
    """
    Validate Trace Agent output by comparing:

        latency_ms

    against:

        baseline_ms

    Example:

        latency_ms  = 1.619
        baseline_ms = 0.119

        ratio = 13.61x

    Therefore the trace is abnormal.
    """

    evidence = _get_evidence(candidate)

    traces = evidence.get(
        "traces",
        []
    )

    if not traces:
        return False

    for trace in traces:

        if not isinstance(trace, dict):
            continue

        latency = _to_float(
            trace.get("latency_ms")
        )

        baseline = _to_float(
            trace.get("baseline_ms")
        )

        status = str(
            trace.get(
                "status",
                trace.get(
                    "severity",
                    ""
                )
            )
        ).lower()

        # ----------------------------------------------
        # Baseline comparison
        # ----------------------------------------------

        if (
            latency is not None
            and baseline is not None
            and baseline > 0
        ):

            ratio = (
                latency / baseline
            )

            if ratio >= LATENCY_RATIO_THRESHOLD:
                return True

        # ----------------------------------------------
        # Explicit trace error
        # ----------------------------------------------

        if status in [
            "error",
            "failed",
            "critical",
        ]:
            return True

    return False


def get_trace_detail(candidate) -> str:

    evidence = _get_evidence(candidate)

    traces = evidence.get(
        "traces",
        []
    )

    if not traces:
        return (
            "Trace Agent returned no trace evidence."
        )

    for trace in traces:

        if not isinstance(trace, dict):
            continue

        service = str(
            trace.get(
                "service",
                "Unknown service"
            )
        )

        operation = str(
            trace.get(
                "operation",
                "Unknown operation"
            )
        )

        latency = _to_float(
            trace.get("latency_ms")
        )

        baseline = _to_float(
            trace.get("baseline_ms")
        )

        if (
            latency is not None
            and baseline is not None
            and baseline > 0
        ):

            ratio = (
                latency / baseline
            )

            if ratio >= LATENCY_RATIO_THRESHOLD:

                return (
                    f"{service} / {operation}: "
                    f"latency={latency:.3f} ms, "
                    f"baseline={baseline:.3f} ms, "
                    f"{ratio:.2f}x baseline. "
                    "Trace anomaly confirmed."
                )

    return (
        "Trace Agent returned trace evidence, "
        "but latency did not exceed the "
        "anomaly threshold."
    )


# ==========================================================
# 4. CONFIDENCE CHECK
# ==========================================================

def check_confidence(candidate) -> bool:

    confidence = _to_float(
        getattr(
            candidate,
            "confidence",
            0.0
        )
    )

    if confidence is None:
        return False

    return (
        confidence >= CONFIDENCE_THRESHOLD
    )


# ==========================================================
# 5. REASON CHECK
# ==========================================================

def check_reason(candidate) -> bool:

    reason = getattr(
        candidate,
        "reason",
        None
    )

    if reason is None:
        reason = getattr(
            candidate,
            "explanation",
            None
        )

    return (
        reason is not None
        and str(reason).strip() != ""
    )


# ==========================================================
# 6. COMPONENT CHECK
# ==========================================================

def check_component(candidate) -> bool:

    component = getattr(
        candidate,
        "component",
        None
    )

    if component is None:
        component = getattr(
            candidate,
            "service",
            None
        )

    return (
        component is not None
        and str(component).strip() != ""
    )


# ==========================================================
# MAIN EVALUATION
# ==========================================================

def evaluate_candidate(candidate) -> ChecklistResult:

    metric_ok = check_metric(candidate)
    log_ok = check_log(candidate)
    trace_ok = check_trace(candidate)

    confidence_ok = check_confidence(
        candidate
    )

    reason_ok = check_reason(
        candidate
    )

    component_ok = check_component(
        candidate
    )

    check_results = {

        "Metric Agent Validation":
            metric_ok,

        "Log Agent Validation":
            log_ok,

        "Trace Agent Validation":
            trace_ok,

        "Confidence Check":
            confidence_ok,

        "Reason Check":
            reason_ok,

        "Component Check":
            component_ok,
    }

    check_details = {

        "Metric Agent Validation":
            get_metric_detail(
                candidate
            ),

        "Log Agent Validation":
            get_log_detail(
                candidate
            ),

        "Trace Agent Validation":
            get_trace_detail(
                candidate
            ),

        "Confidence Check": (
            f"Confidence = "
            f"{float(getattr(candidate, 'confidence', 0.0)):.0%}; "
            f"required >= "
            f"{CONFIDENCE_THRESHOLD:.0%}."
        ),

        "Reason Check": (
            "Root-cause explanation exists."
            if reason_ok
            else
            "Root-cause explanation is missing."
        ),

        "Component Check": (
            "Affected service/component exists."
            if component_ok
            else
            "Affected service/component is missing."
        ),
    }

    score = sum(
        check_results.values()
    )

    failed = [
        name
        for name, passed
        in check_results.items()
        if not passed
    ]

    # ======================================================
    # DECISION
    # ======================================================

    if score == TOTAL_CHECKS:

        return ChecklistResult(
            status="CONFIRMED",
            score=score,
            max_score=TOTAL_CHECKS,
            retry_required=False,
            failed_checks=[],
            recommendation=(
                "All validation checks passed. "
                "The Metric, Log, and Trace Agent outputs "
                "are supported by telemetry evidence."
            ),
            check_results=check_results,
            check_details=check_details,
        )

    if score >= MIN_CHECK_SCORE:

        return ChecklistResult(
            status="RETRY_REQUIRED",
            score=score,
            max_score=TOTAL_CHECKS,
            retry_required=True,
            failed_checks=failed,
            recommendation=(
                "Evidence is partially sufficient. "
                "Re-run Reasoning Agent with additional "
                "telemetry evidence."
            ),
            check_results=check_results,
            check_details=check_details,
        )

    return ChecklistResult(
        status="UNRESOLVED",
        score=score,
        max_score=TOTAL_CHECKS,
        retry_required=False,
        failed_checks=failed,
        recommendation=(
            "Evidence is insufficient to confirm "
            "the root cause."
        ),
        check_results=check_results,
        check_details=check_details,
    )


# ==========================================================
# RETRY CONTROLLER
# ==========================================================

def should_retry(
    result: ChecklistResult,
    retry_count: int,
) -> bool:

    return (
        result.retry_required
        and retry_count < MAX_RETRY
    )


# ==========================================================
# BATCH EVALUATION
# ==========================================================

def evaluate_prediction(prediction):

    results = []

    candidates = getattr(
        prediction,
        "candidates",
        []
    )

    for candidate in candidates:

        results.append(
            evaluate_candidate(
                candidate
            )
        )

    return results
