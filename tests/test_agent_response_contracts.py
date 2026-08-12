import json
from types import SimpleNamespace

import pandas as pd
import pytest

import src.process_module.agents.log_agent as log_module
import src.process_module.agents.metric_agent as metric_module
import src.process_module.agents.trace_agent as trace_module


class _Models:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def generate_content(self, **_kwargs):
        if self.error is not None:
            raise self.error
        return SimpleNamespace(text=json.dumps(self.payload))


class _Client:
    def __init__(self, payload=None, error=None):
        self.models = _Models(payload=payload, error=error)


def _agent(agent_class, *, payload=None, error=None):
    agent = object.__new__(agent_class)
    agent.client = _Client(payload=payload, error=error)
    agent.model_name = "offline-test-model"
    return agent


def _context():
    return SimpleNamespace(
        investigation_id=1,
        service="order-service",
        incident_time="2021-03-25 09:03:00",
    )


AGENT_CASES = (
    (
        metric_module,
        metric_module.MetricAgent,
        "get_investigation_metrics",
        pd.DataFrame(
            [
                {
                    "timestamp": "2021-03-25 09:03:00",
                    "cmdb_id": "order-service",
                    "kpi_name": "cpu",
                    "value": 30.0,
                }
            ]
        ),
        "anomalies",
    ),
    (
        log_module,
        log_module.LogAgent,
        "get_investigation_logs",
        pd.DataFrame(
            [
                {
                    "timestamp": "2021-03-25 09:03:00",
                    "cmdb_id": "order-service",
                    "value": "fatal timeout error",
                }
            ]
        ),
        "logs",
    ),
    (
        trace_module,
        trace_module.TraceAgent,
        "get_investigation_traces",
        pd.DataFrame(
            [
                {
                    "timestamp": "2021-03-25 09:03:00",
                    "cmdb_id": "order-service",
                    "span_id": "span-1",
                    "trace_id": "trace-1",
                    "duration": 1_000,
                    "type": "server",
                    "status_code": "0",
                    "operation_name": "checkout",
                    "parent_span": "parent-1",
                }
            ]
        ),
        "traces",
    ),
)


@pytest.mark.parametrize("payload", [[], True, "not-an-object"])
@pytest.mark.parametrize(
    ("module", "agent_class", "loader_name", "frame", "evidence_key"),
    AGENT_CASES,
)
def test_valid_json_primitives_use_mapping_fallback(
    monkeypatch,
    payload,
    module,
    agent_class,
    loader_name,
    frame,
    evidence_key,
):
    monkeypatch.setattr(module, loader_name, lambda *_args, **_kwargs: frame)

    result = _agent(agent_class, payload=payload).analyze(_context())

    assert isinstance(result, dict)
    assert isinstance(result[evidence_key], list)


def test_metric_fallback_preserves_measured_values(monkeypatch):
    frame = pd.DataFrame(
        [
            {
                "timestamp": "2021-03-25 09:02:00",
                "cmdb_id": "order-service",
                "kpi_name": "cpu",
                "value": 10.0,
            },
            {
                "timestamp": "2021-03-25 09:03:00",
                "cmdb_id": "order-service",
                "kpi_name": "cpu",
                "value": 30.0,
            },
        ]
    )
    monkeypatch.setattr(
        metric_module,
        "get_investigation_metrics",
        lambda *_args, **_kwargs: frame,
    )

    result = _agent(
        metric_module.MetricAgent,
        error=RuntimeError("offline model"),
    ).analyze(_context())

    anomaly = result["anomalies"][0]
    assert anomaly["value"] == 30.0
    assert anomaly["baseline"] == 20.0
    assert anomaly["timestamp"] == "2021-03-25 09:03:00"
