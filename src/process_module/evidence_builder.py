from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import pandas as pd

from src.schemas import TimeWindow


# ======================================================
# STEP 8.3 SCHEMA
# ======================================================

@dataclass
class InvestigationContext:
    """
    Investigation context for ONE logical service.

    This object is passed directly to
    Metric / Log / Trace Agents.
    """

    dataset: str
    service: str
    incident_time: datetime
    time_window: TimeWindow

    metrics: Dict[str, pd.DataFrame]
    logs: Dict[str, pd.DataFrame]
    traces: Dict[str, pd.DataFrame]


# ======================================================
# STEP 8.3
# ======================================================

def build_investigation_context(
    telemetry,
    service_links,
    parsed_query,
):
    """
    Build investigation context for every logical service.

    Parameters
    ----------
    telemetry
        Output from telemetry preprocessing.

        Expected structure:
            telemetry.metrics
            telemetry.logs
            telemetry.traces

    service_links
        Output from build_service_links().

        Structure:
            {
                "checkoutservice": {
                    "metrics": ["metric_service"],
                    "logs": ["log_service"],
                    "traces": ["trace_service"],
                },
                ...
            }

    parsed_query
        Parsed incident information.

    Returns
    -------
    dict
        {
            "checkoutservice": InvestigationContext(...),
            "shippingservice": InvestigationContext(...),
            ...
        }
    """

    contexts = {}

    # ==================================================
    # Debug
    # ==================================================

    print("\n==============================")
    print("BUILD INVESTIGATION CONTEXT")
    print("==============================")

    print(
        "Telemetry metric keys:",
        list(telemetry.metrics.keys()),
    )

    print(
        "Telemetry log keys:",
        list(telemetry.logs.keys()),
    )

    print(
        "Telemetry trace keys:",
        list(telemetry.traces.keys()),
    )

    print(
        "Logical services:",
        len(service_links),
    )

    # ==================================================
    # Build context for each logical service
    # ==================================================

    for service, links in sorted(service_links.items()):

        print("\n------------------------------")
        print("SERVICE:", service)

        # ----------------------------------------------
        # Metrics
        # ----------------------------------------------

        metric_dict = {}

        for metric_file in links.get("metrics", []):

            if metric_file not in telemetry.metrics:
                print(
                    f"WARNING: Metric dataset not found: "
                    f"{metric_file}"
                )
                continue

            df = telemetry.metrics[metric_file]

            if df is None:
                print(
                    f"WARNING: Metric dataset is None: "
                    f"{metric_file}"
                )
                continue

            metric_dict[metric_file] = df

        # ----------------------------------------------
        # Logs
        # ----------------------------------------------

        log_dict = {}

        for log_file in links.get("logs", []):

            if log_file not in telemetry.logs:
                print(
                    f"WARNING: Log dataset not found: "
                    f"{log_file}"
                )
                continue

            df = telemetry.logs[log_file]

            if df is None:
                print(
                    f"WARNING: Log dataset is None: "
                    f"{log_file}"
                )
                continue

            log_dict[log_file] = df

        # ----------------------------------------------
        # Traces
        # ----------------------------------------------

        trace_dict = {}

        for trace_file in links.get("traces", []):

            if trace_file not in telemetry.traces:
                print(
                    f"WARNING: Trace dataset not found: "
                    f"{trace_file}"
                )
                continue

            df = telemetry.traces[trace_file]

            if df is None:
                print(
                    f"WARNING: Trace dataset is None: "
                    f"{trace_file}"
                )
                continue

            trace_dict[trace_file] = df

        # ----------------------------------------------
        # Debug
        # ----------------------------------------------

        print("Metrics:", list(metric_dict.keys()))
        print("Logs:", list(log_dict.keys()))
        print("Traces:", list(trace_dict.keys()))

        # ----------------------------------------------
        # Create InvestigationContext
        # ----------------------------------------------

        contexts[service] = InvestigationContext(
            dataset=telemetry.dataset,
            service=service,
            incident_time=parsed_query.incident_time,
            time_window=parsed_query.time_window,
            metrics=metric_dict,
            logs=log_dict,
            traces=trace_dict,
        )

    # ==================================================
    # Summary
    # ==================================================

    print("\n==============================")
    print("INVESTIGATION CONTEXT RESULT")
    print("==============================")

    for service, context in sorted(contexts.items()):

        print("\nSERVICE:", service)

        print(
            "Metrics:",
            list(context.metrics.keys()),
        )

        print(
            "Logs:",
            list(context.logs.keys()),
        )

        print(
            "Traces:",
            list(context.traces.keys()),
        )

    print(
        "\nTotal contexts:",
        len(contexts),
    )

    return contexts