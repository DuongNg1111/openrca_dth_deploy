import os

if __name__ != "__main__":
    import pytest

    pytest.skip("manual PostgreSQL integration script", allow_module_level=True)
elif os.getenv("OPENRCA_RUN_MUTATING_TESTS") != "1":
    raise SystemExit(
        "Set OPENRCA_RUN_MUTATING_TESTS=1 to run this database-writing script."
    )

import pandas as pd

from src.database.repository import insert_metrics

df = pd.DataFrame(
    [
        {
            "timestamp": 1647759600,
            "cmdb_id": "node-6.adservice2-0",
            "kpi_name": "container_network_receive_packets_dropped.eth0",
            "value": 0.0
        },
        {
            "timestamp": 1647759660,
            "cmdb_id": "node-6.adservice2-0",
            "kpi_name": "container_network_receive_packets_dropped.eth0",
            "value": 0.0
        }
    ]
)


insert_metrics(
    investigation_id=1,
    dataframe=df
)


print("Metric inserted")
