import os
from types import SimpleNamespace

import pandas as pd
import pytest

from src.process_module.agents.reasoning_agent import ReasoningAgent

if os.getenv("OPENRCA_RUN_INTEGRATION_TESTS") != "1":
    pytest.skip("requires explicit Gemini integration opt-in", allow_module_level=True)


def test_reasoning_agent():
    context = SimpleNamespace(
        investigation_id="INV-001",
        service="payment-service",
        incident_time="2021-03-25 10:00:00",
        incident_description="Payment service is slow and requests are timing out",
    )

    evidence_df = pd.DataFrame(
        [
            {
                "evidence_type": "metric",
                "service": "payment-service",
                "description": "CPU usage is high",
                "score": 0.9,
            },
            {
                "evidence_type": "log",
                "service": "payment-service",
                "description": "Many timeout errors",
                "score": 0.9,
            },
            {
                "evidence_type": "trace",
                "service": "payment-service",
                "description": "payment-service slow",
                "score": 0.9,
            },
        ]
    )

    agent = ReasoningAgent()

    result = agent.analyze(
        context,
        evidence_df,
    )

    assert isinstance(result, dict)

    assert "agent" in result
    assert result["agent"] == "Reasoning Agent"

    assert "root_cause" in result
    assert "confidence" in result
    assert "explanation" in result
    assert "supporting_evidence" in result

    assert isinstance(result["root_cause"], str)

    assert isinstance(
        result["confidence"],
        (int, float),
    )

    assert 0 <= result["confidence"] <= 100

    assert isinstance(
        result["supporting_evidence"],
        list,
    )


def test_reasoning_agent_empty_evidence():
    context = SimpleNamespace(
        investigation_id="INV-002",
        service="payment-service",
        incident_time="2021-03-25 10:00:00",
        incident_description="Payment service is unavailable",
    )

    evidence_df = pd.DataFrame()

    agent = ReasoningAgent()

    result = agent.analyze(
        context,
        evidence_df,
    )

    assert result["agent"] == "Reasoning Agent"
    assert result["root_cause"] == "Insufficient evidence"
    assert result["confidence"] == 0.0


def test_reasoning_agent_no_evidence():
    context = SimpleNamespace(
        investigation_id="INV-003",
        service="payment-service",
        incident_time="2021-03-25 10:00:00",
        incident_description="Payment service is unavailable",
    )

    agent = ReasoningAgent()

    result = agent.analyze(
        context,
        None,
    )

    assert result["agent"] == "Reasoning Agent"
    assert result["root_cause"] == "Insufficient evidence"
    assert result["confidence"] == 0.0
