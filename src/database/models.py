from dataclasses import dataclass
from datetime import datetime


# =====================================================
# Investigation Case
# =====================================================

@dataclass
class InvestigationCase:
    issue_key: str
    environment: str
    dataset: str
    incident_time: datetime
    window_start: datetime
    window_end: datetime


# =====================================================
# Service Context Record
# =====================================================

@dataclass
class ServiceContextRecord:
    """
    Lightweight context used to identify the investigation
    and service that an Agent should analyze.

    Telemetry data is NOT stored here.
    Agents query PostgreSQL using investigation_id.
    """

    issue_key: str
    service: str
    investigation_id: int


# =====================================================
# Trace Dependency Record
# =====================================================

@dataclass
class TraceDependencyRecord:
    issue_key: str
    trace_id: str
    parent_service: str
    child_service: str