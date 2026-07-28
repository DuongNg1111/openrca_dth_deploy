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