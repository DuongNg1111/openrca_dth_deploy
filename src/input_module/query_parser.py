"""INPUT module - Parse Jira RawQuery into structured ParsedQuery."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from src.schemas import RawQuery, TimeWindow
from datetime import datetime

# Extract datetime from Jira format:
# 2022-03-20T20:30:00.000+0700
_DATETIME = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})T"
    r"(\d{2}):(\d{2}):(\d{2})"
)


@dataclass
class ParsedQuery:
    """
    Structured query after parsing Jira issue.
    """
    issue_key: str
    environment: str
    incident_description: str
    affected_system: str
    incident_time: str
    additional_information: str
    keywords: list[str] = field(default_factory=list)
    time_window: TimeWindow | None = None


def _extract_keywords(text: str) -> list[str]:
    """
    Simple keyword extraction.
    """

    words = re.findall(
        r"[a-zA-Z]+",
        text.lower()
    )

    stop_words = {
        "the",
        "a",
        "an",
        "at",
        "to",
        "and",
        "of",
        "in",
        "is",
        "was",
    }

    keywords = [
        w
        for w in words
        if w not in stop_words
    ]

    return keywords


def _parse_incident_time(
    incident_time: str
) -> tuple[datetime, TimeWindow]:

    match = _DATETIME.search(incident_time)

    if not match:
        raise ValueError(
            f"Invalid incident time: {incident_time}"
        )

    year, month, day, hour, minute, second = (
        int(x)
        for x in match.groups()
    )

    dt = datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
    )

    window = TimeWindow(
        start=dt - timedelta(minutes=15),
        end=dt + timedelta(minutes=15),
    )

    return dt, window



def parse_query(
    raw_query: RawQuery
) -> ParsedQuery:
    """
    Convert RawQuery from Jira
    into ParsedQuery.

    Pipeline:

        Jira
          |
          v
       RawQuery
          |
          v
     ParsedQuery
    """

    incident_dt, window = _parse_incident_time(
    raw_query.incident_time
)


    combined_text = " ".join(
    [
        raw_query.incident_description or "",
        raw_query.additional_information or "",
        raw_query.affected_system or "",
    ]
)


    keywords = _extract_keywords(
        combined_text
    )


    parsed = ParsedQuery(

        issue_key=raw_query.issue_key,

        environment=raw_query.environment,

        incident_description=
            raw_query.incident_description,

        affected_system=
            raw_query.affected_system,

        incident_time=incident_dt,

        additional_information=
            raw_query.additional_information,

        keywords=keywords,

        time_window=window,
)


    return parsed