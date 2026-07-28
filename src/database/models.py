from dataclasses import dataclass
from datetime import datetime
from typing import List


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

    issue_key: str

    service: str

    metric_files: List[str]

    log_files: List[str]

    trace_files: List[str]


# =====================================================
# Trace Dependency Record
# =====================================================

@dataclass
class TraceDependencyRecord:

    issue_key: str

    trace_id: str

    parent_service: str

    child_service: str