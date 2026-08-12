import pytest

from src.input_module.query_parser import parse_query
from src.schemas import ParsedQuery, RawQuery


def test_text_query_keeps_mock_pipeline_contract():
    window, hints = parse_query("Incident on 2021-03-25 from 09:00 to 09:30")

    assert window.start.isoformat() == "2021-03-25T09:00:00"
    assert window.end.isoformat() == "2021-03-25T09:30:00"
    assert hints == []


def test_raw_query_keeps_full_pipeline_contract():
    raw_query = RawQuery(
        issue_key="TEST-1",
        incident_description="Order requests time out",
        affected_system="Order",
        environment="Cloud A",
        incident_time="2022-03-20T20:30:00.000+0700",
    )

    parsed = parse_query(raw_query)

    assert isinstance(parsed, ParsedQuery)
    assert parsed.issue_key == "TEST-1"
    assert parsed.time_window.start.isoformat() == "2022-03-20T20:15:00"
    assert "order" in parsed.keywords


def test_obvious_midnight_rollover_uses_the_next_day():
    window, _ = parse_query("Incident on 2021-03-25 from 23:50 to 00:10")

    assert window.start.isoformat() == "2021-03-25T23:50:00"
    assert window.end.isoformat() == "2021-03-26T00:10:00"


def test_ambiguous_reversed_window_is_rejected():
    with pytest.raises(ValueError, match="end time must be after start time"):
        parse_query("Incident on 2021-03-25 from 10:30 to 09:00")
