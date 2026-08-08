from types import SimpleNamespace

from src.process_module.agents.reasoning_agent import ReasoningAgent


def test_reasoning_agent():

    context = SimpleNamespace(
        service="payment-service",
        incident_time="2021-03-25 10:00:00"
    )

    agent = ReasoningAgent()

    result = agent.analyze(

        context,

        {
            "anomalies": [
                "CPU high"
            ],
            "summary": "CPU usage is high"
        },

        {
            "errors": [
                "timeout"
            ],
            "summary": "Many timeout errors"
        },

        {
            "traces": [
                "payment-service slow"
            ],
            "summary": "Slow trace detected"
        }

    )

    assert "reason" in result
    assert "confidence" in result
    assert result["component"] == "payment-service"