from dataclasses import dataclass
from datetime import datetime

from src.schemas import TimeWindow


# ======================================================
# INVESTIGATION CONTEXT
# ======================================================

@dataclass
class InvestigationContext:
    """
    Investigation context for ONE logical service.

    Agents use investigation_id to query telemetry
    directly from PostgreSQL.
    """

    investigation_id: int
    dataset: str
    service: str
    incident_time: datetime
    time_window: TimeWindow


# ======================================================
# BUILD INVESTIGATION CONTEXT
# ======================================================

def build_investigation_context(
    telemetry,
    service_links,
    parsed_query,
    investigation_id,
):
    """
    Build investigation context for every logical service.

    IMPORTANT:
    This function does NOT pass preprocessed telemetry
    DataFrames to agents.

    Agents must query PostgreSQL using investigation_id.
    """

    contexts = {}

    # ==================================================
    # Debug
    # ==================================================

    print("\n==============================")
    print("BUILD INVESTIGATION CONTEXT")
    print("==============================")

    print(
        "Investigation ID:",
        investigation_id,
    )

    print(
        "Dataset:",
        telemetry.dataset,
    )

    print(
        "Logical services:",
        len(service_links),
    )

    # ==================================================
    # Build context for each logical service
    # ==================================================

    for service in sorted(service_links.keys()):

        print("\n------------------------------")
        print("SERVICE:", service)

        contexts[service] = InvestigationContext(
            investigation_id=investigation_id,
            dataset=telemetry.dataset,
            service=service,
            incident_time=parsed_query.incident_time,
            time_window=parsed_query.time_window,
        )

        print(
            "Investigation ID:",
            contexts[service].investigation_id,
        )

        print(
            "Incident Time:",
            contexts[service].incident_time,
        )

        print(
            "Window:",
            contexts[service].time_window.start,
            "->",
            contexts[service].time_window.end,
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
            "Investigation ID:",
            context.investigation_id,
        )

        print(
            "Dataset:",
            context.dataset,
        )

        print(
            "Incident Time:",
            context.incident_time,
        )

        print(
            "Window:",
            context.time_window.start,
            "->",
            context.time_window.end,
        )

    print(
        "\nTotal contexts:",
        len(contexts),
    )

    return contexts