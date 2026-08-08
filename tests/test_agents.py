from __future__ import annotations

import json
from datetime import datetime

from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent


# =====================================================
# TEST CONFIG
# =====================================================

INVESTIGATION_ID = 68
SERVICE = "frontend-0"

INCIDENT_TIME = datetime(
    2022,
    3,
    20,
    10,
    13,
    12,
)


# =====================================================
# TEST CONTEXT
# =====================================================

class TestContext:

    def __init__(
        self,
        investigation_id,
        service,
        incident_time,
    ):
        self.investigation_id = investigation_id
        self.service = service
        self.incident_time = incident_time


context = TestContext(
    investigation_id=INVESTIGATION_ID,
    service=SERVICE,
    incident_time=INCIDENT_TIME,
)


# =====================================================
# PRINT RESULT
# =====================================================

def print_result(
    agent_name,
    result,
):

    print("\n" + "=" * 70)
    print(agent_name)
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


# =====================================================
# 1. TEST METRIC AGENT
# =====================================================

print("\n[1/3] Testing Metric Agent...")

try:

    metric_agent = MetricAgent()

    metric_result = metric_agent.analyze(
        context
    )

    print_result(
        "METRIC AGENT RESULT",
        metric_result,
    )

except Exception as e:

    print("\nMetric Agent FAILED")

    print(
        type(e).__name__,
        str(e),
    )


# =====================================================
# 2. TEST LOG AGENT
# =====================================================

print("\n[2/3] Testing Log Agent...")

try:

    log_agent = LogAgent()

    log_result = log_agent.analyze(
        context
    )

    print_result(
        "LOG AGENT RESULT",
        log_result,
    )

except Exception as e:

    print("\nLog Agent FAILED")

    print(
        type(e).__name__,
        str(e),
    )


# =====================================================
# 3. TEST TRACE AGENT
# =====================================================

print("\n[3/3] Testing Trace Agent...")

try:

    trace_agent = TraceAgent()

    trace_result = trace_agent.analyze(
        context
    )

    print_result(
        "TRACE AGENT RESULT",
        trace_result,
    )

except Exception as e:

    print("\nTrace Agent FAILED")

    print(
        type(e).__name__,
        str(e),
    )


# =====================================================
# END
# =====================================================

print("\n" + "=" * 70)
print("AGENT TEST COMPLETED")
print("=" * 70)
print(
    "Investigation ID:",
    INVESTIGATION_ID,
)
print(
    "Service:",
    SERVICE,
)
print("Full pipeline was NOT executed.")