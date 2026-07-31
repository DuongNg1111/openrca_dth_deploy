import pandas as pd

from types import SimpleNamespace
from src.process_module.link_telemetry import build_service_links


def test_service_links_metric():

    telemetry = SimpleNamespace()

    telemetry.metrics = {
        "metric_service": pd.DataFrame(
            {
                "timestamp": [
                    1647771000000
                ],
                "cmdb_id": [
                    "productcatalogservice"
                ],
                "kpi_name": [
                    "rr"
                ],
                "value": [
                    10
                ]
            }
        )
    }


    telemetry.logs = {}

    telemetry.traces = {}


    links = build_service_links(
        telemetry
    )


    print("\n====================")
    print(links)


    assert (
        "productcatalogservice"
        in links
    )


    assert (
        "metric_service"
        in links["productcatalogservice"]["metrics"]
    )