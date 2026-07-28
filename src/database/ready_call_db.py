from src.database.models import (
    InvestigationCase,
    ServiceContextRecord,
)


# =====================================================
# Temporary Ready-To-Call Database
# =====================================================

READY_TO_CALL_DB = {
    "cases": [],
    "services": [],
}


# =====================================================
# Step 8.4
# Store Ready-To-Call Data
# =====================================================

def store_ready_call_data(
    parsed_query,
    telemetry,
    contexts,
):
    """
    Store investigation context into Ready-To-Call Database.

    Parameters
    ----------
    parsed_query

    telemetry
        Output from preprocess()

    contexts
        Output from build_investigation_context()
    """

    # ---------------------------------------
    # Investigation Case
    # ---------------------------------------

    case = InvestigationCase(

        issue_key=parsed_query.issue_key,

        environment=parsed_query.environment,

        dataset=telemetry.dataset,

        incident_time=parsed_query.incident_time,

        window_start=parsed_query.time_window.start,

        window_end=parsed_query.time_window.end,
    )

    READY_TO_CALL_DB["cases"].append(case)

    # ---------------------------------------
    # Service Context
    # ---------------------------------------

    for service, context in contexts.items():

        READY_TO_CALL_DB["services"].append(

            ServiceContextRecord(

                issue_key=parsed_query.issue_key,

                service=service,

                metric_files=list(context.metrics.keys()),

                log_files=list(context.logs.keys()),

                trace_files=list(context.traces.keys()),
            )
        )

    return READY_TO_CALL_DB