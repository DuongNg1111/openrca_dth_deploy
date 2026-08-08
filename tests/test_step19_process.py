from types import SimpleNamespace

import pandas as pd

from src.process_module.orchestrator import ProcessOrchestrator


def test_step19_process():

    context = SimpleNamespace()

    context.service = "payment-service"

    context.incident_time = "2021-03-25 10:00:00"

    metric_df = pd.DataFrame({

        "kpi_name":[
            "cpu_usage",
            "cpu_usage",
            "cpu_usage"
        ],

        "value":[
            40,
            60,
            95
        ]

    })

    log_df = pd.DataFrame({

        "message":[
            "Database timeout",
            "Connection error",
            "Normal request"
        ]

    })

    trace_df = pd.DataFrame({

        "trace_id":[
            "abc"
        ],

        "duration":[
            2500
        ],

        "service":[
            "payment-service"
        ]

    })

    context.metrics = {

        "metric.csv":metric_df

    }

    context.logs = {

        "log.csv":log_df

    }

    context.traces = {

        "trace.csv":trace_df

    }

    orchestrator = ProcessOrchestrator()

    result = orchestrator.run(context)

    assert "reason" in result

    assert "confidence" in result

    assert "reasoning" in result

    assert "component" in result

    assert "metrics" in result

    assert "logs" in result

    assert "traces" in result