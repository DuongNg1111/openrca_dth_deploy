from datetime import datetime, timedelta

from src.database.repository import create_investigation


investigation_id = create_investigation(
    issue_key="TEST-001",
    environment="cloudbed",
    dataset="cloudbed-1",
    incident_time=datetime.now(),
    window_start=datetime.now() - timedelta(minutes=15),
    window_end=datetime.now() + timedelta(minutes=15),
    incident_description="Testing database repository"
)


print(
    "Created investigation:",
    investigation_id
)