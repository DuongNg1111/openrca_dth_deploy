"""INPUT module - Parse Jira RawQuery into structured ParsedQuery."""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from src.schemas import (
    ParsedQuery,
    RawQuery,
    TimeWindow,
)

# Extract datetime from Jira format:
# 2022-03-20T20:30:00.000+0700
_DATETIME = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})[ T]"
    r"(\d{2}):(\d{2}):(\d{2})"
)
_DATE = re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})")
_TIME = re.compile(r"(\d{1,2}):(\d{2})")


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
    incident_time: str | None,
    created: str | None = None,
) -> tuple[datetime, TimeWindow]:

    # Nếu incident_time rỗng thì dùng created của Jira
    incident_time = incident_time or created

    if incident_time is None:
        raise ValueError(
            "Both incident_time and created are missing."
        )

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


def _parse_natural_language_query(
    query: str,
    default_date: str,
) -> tuple[TimeWindow, list[str]]:
    """Parse the simple natural-language query used by the mock quickstart."""
    date_match = _DATE.search(query)
    if date_match:
        year, month, day = (int(value) for value in date_match.groups())
    else:
        year, month, day = (int(value) for value in default_date.split("-"))

    times = _TIME.findall(query)
    if len(times) >= 2:
        start_hour, start_minute = (int(value) for value in times[0])
        end_hour, end_minute = (int(value) for value in times[1])
    elif len(times) == 1:
        start_hour, start_minute = (int(value) for value in times[0])
        start = datetime(year, month, day, start_hour, start_minute)
        return TimeWindow(start=start, end=start + timedelta(minutes=30)), []
    else:
        start_hour, start_minute, end_hour, end_minute = 9, 0, 9, 30

    start = datetime(year, month, day, start_hour, start_minute)
    end = datetime(year, month, day, end_hour, end_minute)
    if end <= start:
        if start_hour >= 18 and end_hour <= 6:
            end += timedelta(days=1)
        else:
            raise ValueError(
                "Query end time must be after start time; only obvious "
                "evening-to-early-morning ranges are treated as overnight."
            )

    return (
        TimeWindow(start=start, end=end),
        [],
    )


def _parse_raw_query(raw_query: RawQuery) -> ParsedQuery:
    """Convert a Jira ``RawQuery`` into the full-pipeline contract."""

    incident_dt, window = _parse_incident_time(
        raw_query.incident_time,
        raw_query.created,
    )

    combined_text = " ".join([
        raw_query.incident_description or "",
        raw_query.affected_system or "",
    ])

    keywords = _extract_keywords(combined_text)

    parsed = ParsedQuery(
        issue_key=raw_query.issue_key,
        environment=raw_query.environment,
        incident_description=raw_query.incident_description,
        affected_system=raw_query.affected_system,
        incident_time=incident_dt,
        keywords=keywords,
        time_window=window,
        additional_information=raw_query.additional_information,
    )

    return parsed


def parse_query(
    query: RawQuery | str,
    default_date: str = "2021-03-25",
) -> ParsedQuery | tuple[TimeWindow, list[str]]:
    """Parse either a Jira query or the mock quickstart's text query.

    Supporting both contracts keeps the full Jira pipeline intact while the
    lightweight teaching pipeline remains runnable without Jira or a dataset.
    """
    if isinstance(query, str):
        return _parse_natural_language_query(query, default_date)
    if isinstance(query, RawQuery):
        return _parse_raw_query(query)
    raise TypeError("query must be a RawQuery or str")
