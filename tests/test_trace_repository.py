import os

if __name__ != "__main__":
    import pytest

    pytest.skip("manual PostgreSQL integration script", allow_module_level=True)
elif os.getenv("OPENRCA_RUN_MUTATING_TESTS") != "1":
    raise SystemExit(
        "Set OPENRCA_RUN_MUTATING_TESTS=1 to run this database-writing script."
    )

import pandas as pd

from src.database.repository import insert_traces

df = pd.DataFrame(
    [
        {
            "timestamp":1647705600395,
            "cmdb_id":"currencyservice-1",
            "span_id":"cf4f12dee7b2b1d8",
            "trace_id":"7b532f0b62717b83b9d3ff72e97447c2",
            "duration":120,
            "type":"telemetry",
            "status_code":0,
            "operation_name":"grpc.hipstershop.CurrencyService/Convert",
            "parent_span":"dc3292f5e193a9a3"
        }
    ]
)


insert_traces(
    investigation_id=1,
    dataframe=df
)


print("Traces inserted")
