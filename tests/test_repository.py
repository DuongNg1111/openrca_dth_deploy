import os

if __name__ != "__main__":
    import pytest

    pytest.skip("manual PostgreSQL integration script", allow_module_level=True)
elif os.getenv("OPENRCA_RUN_MUTATING_TESTS") != "1":
    raise SystemExit(
        "Set OPENRCA_RUN_MUTATING_TESTS=1 to run this database-writing script."
    )

from datetime import datetime, timedelta

from src.database.repository import create_investigation

investigation_id = create_investigation(
    issue_key="TEST-001",
    environment="cloudbed",
    affected_system="Order",
    dataset="cloudbed-1",
    incident_time=datetime.now(),
    window_start=datetime.now() - timedelta(minutes=15),
    window_end=datetime.now() + timedelta(minutes=15),
    incident_description="Testing database repository",
    reporter="Capstone Reviewer",
    reporter_email="",
)


print(
    "Created investigation:",
    investigation_id
)
