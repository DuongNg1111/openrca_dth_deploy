"""INPUT module — turn a natural-language failure query into structured fields."""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from src.schemas import TimeWindow

_DATE = re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})")
_TIME = re.compile(r"(\d{1,2}):(\d{2})")


def parse_query(query: str, default_date: str = "2021-03-25"):
    """Heuristic parser -> (TimeWindow, components_hint).

    TODO(DEV 1): for messy queries, optionally add an LLM extraction step.
    """
    m = _DATE.search(query)
    if m:
        y, mo, d = (int(x) for x in m.groups())
    else:
        y, mo, d = (int(x) for x in default_date.split("-"))

    times = _TIME.findall(query)
    if len(times) >= 2:
        sh, sm = int(times[0][0]), int(times[0][1])
        eh, em = int(times[1][0]), int(times[1][1])
    elif len(times) == 1:
        sh, sm = int(times[0][0]), int(times[0][1])
        # eh, em = sh, min(59, sm + 30)
    else:
        sh, sm, eh, em = 9, 0, 9, 30

    incident_time = datetime(y, mo, d, sh, sm)

    window_start = incident_time - timedelta(minutes=15)
    window_end = incident_time + timedelta(minutes=15)

    return TimeWindow(window_start, window_end), []
