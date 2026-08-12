from pathlib import Path

from src.database.table_schemas import TABLE_SCHEMAS

ROOT = Path(__file__).resolve().parents[1]


def test_tracked_database_contract_matches_repository_datetime_inserts():
    for table in ("investigation_metrics", "investigation_logs", "investigation_traces"):
        assert TABLE_SCHEMAS[table]["columns"]["timestamp"] == "TIMESTAMP"

    schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
    assert '"timestamp" bigint' not in schema
    assert schema.count('"timestamp" timestamp without time zone') >= 4


def test_tracked_database_contract_contains_current_pipeline_columns():
    investigation_columns = TABLE_SCHEMAS["investigations"]["columns"]
    assert {"affected_system", "reporter", "reporter_email", "status", "created_at"}.issubset(
        investigation_columns
    )

    evidence_columns = TABLE_SCHEMAS["evidence_records"]["columns"]
    assert {
        "metric_name",
        "trace_id",
        "operation",
        "value",
        "baseline",
        "timestamp",
        "confidence",
        "created_at",
        "metadata",
    }.issubset(evidence_columns)
