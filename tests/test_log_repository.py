import os

if __name__ != "__main__":
    import pytest

    pytest.skip("manual PostgreSQL integration script", allow_module_level=True)
elif os.getenv("OPENRCA_RUN_MUTATING_TESTS") != "1":
    raise SystemExit(
        "Set OPENRCA_RUN_MUTATING_TESTS=1 to run this database-writing script."
    )

import pandas as pd

from src.database.repository import insert_logs

df = pd.DataFrame(
    [
        {
            "log_id": "test-log-001",
            "timestamp": 1647734485,
            "cmdb_id": "adservice-0",
            "log_name": "log_adservice-envoy_gateway",
            "value": "POST request success"
        },
        {
            "log_id": "test-log-002",
            "timestamp": 1647734490,
            "cmdb_id": "currencyservice-0",
            "log_name": "log_currencyservice-service_application",
            "value": "conversion request successful"
        }
    ]
)


insert_logs(
    investigation_id=1,
    dataframe=df
)


print("Logs inserted")
