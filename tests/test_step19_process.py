import os
from types import SimpleNamespace

import pytest

from src.process_module.orchestrator import ProcessOrchestrator

if (
    os.getenv("OPENRCA_RUN_INTEGRATION_TESTS") != "1"
    or os.getenv("OPENRCA_RUN_MUTATING_TESTS") != "1"
    or not os.getenv("OPENRCA_TEST_INVESTIGATION_ID")
):
    pytest.skip(
        "requires explicit PostgreSQL/Gemini and mutating-test opt-ins",
        allow_module_level=True,
    )


def test_step19_process():
    investigation_id = int(os.environ["OPENRCA_TEST_INVESTIGATION_ID"])
    context = SimpleNamespace(
        investigation_id=investigation_id,
        service=os.getenv("OPENRCA_TEST_SERVICE", "payment-service"),
        incident_time="2021-03-25 10:00:00",
        incident_description="Payment service failure",
    )

    result = ProcessOrchestrator().run(
        context,
        investigation_id=investigation_id,
    )

    assert result["agent"] == "Reasoning Agent"
    assert "root_cause" in result
    assert "confidence" in result
    assert "explanation" in result
