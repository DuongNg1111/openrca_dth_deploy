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
    Investigation context for ONE service.

    This object will be passed directly
    to Metric / Log / Trace Agents.
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
    Build investigation context for every service.

    Parameters
    ----------
    telemetry
        Output from Step 7 (preprocess).

    service_links
        Output from Step 8.2.

    parsed_query
        Parsed incident information.

    Returns
    -------
    dict

    {
        "shippingservice":
            InvestigationContext(...),

        "paymentservice":
            InvestigationContext(...),
    }
    """

    contexts = {}

    for service, links in service_links.items():

        metric_dict = {}

        log_dict = {}

        trace_dict = {}

        # ---------------------------------------
        # Metrics
        # ---------------------------------------

        for metric_file in links["metrics"]:
            if metric_file in telemetry.metrics:
                metric_dict[metric_file] = (
                    telemetry.metrics[metric_file]
                )

        # ---------------------------------------
        # Logs
        # ---------------------------------------

        for log_file in links["logs"]:
            if log_file in telemetry.logs:
                log_dict[log_file] = (
                    telemetry.logs[log_file]
                )

        # ---------------------------------------
        # Traces
        # ---------------------------------------

        for trace_file in links["traces"]:
            if trace_file in telemetry.traces:
                trace_dict[trace_file] = (
                    telemetry.traces[trace_file]
                )

        contexts[service] = InvestigationContext(
            dataset=telemetry.dataset,
            service=service,
            incident_time=parsed_query.incident_time,
            time_window=parsed_query.time_window,
            metrics=metric_dict,
            logs=log_dict,
            traces=trace_dict,
        )

    return contexts