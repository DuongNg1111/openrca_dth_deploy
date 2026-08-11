import pandas as pd

from src.process_module.transform import (
    aggregate_metrics,
    metrics_to_features,
)


def main():

    print("\n========================================")
    print("TEST TRANSFORM")
    print("========================================")

    df = pd.DataFrame(
        [
            {
                "timestamp": "2022-03-20 14:10:00",
                "cmdb_id": "node-5.cartservice-0",
                "kpi_name": "cpu_usage",
                "value": 20,
            },
            {
                "timestamp": "2022-03-20 14:11:00",
                "cmdb_id": "node-5.cartservice-0",
                "kpi_name": "cpu_usage",
                "value": 30,
            },
            {
                "timestamp": "2022-03-20 14:12:00",
                "cmdb_id": "node-5.cartservice-0",
                "kpi_name": "cpu_usage",
                "value": 40,
            },
            {
                "timestamp": "2022-03-20 14:10:00",
                "cmdb_id": "node-5.frontend-0",
                "kpi_name": "cpu_usage",
                "value": 50,
            },
        ]
    )

    print("\nINPUT:")
    print(df)

    features = metrics_to_features(
        df
    )

    print("\nFEATURES:")

    for key, value in features.items():

        print("\nSERVICE / KPI:")
        print(key)

        print("Values:")
        print(value["values"])

        print("N:")
        print(value["n"])

    # =========================================
    # Assertions
    # =========================================

    assert (
        "node-5.cartservice-0",
        "cpu_usage",
    ) in features

    assert (
        "node-5.frontend-0",
        "cpu_usage",
    ) in features

    assert features[
        (
            "node-5.cartservice-0",
            "cpu_usage",
        )
    ]["values"] == [
        20.0,
        30.0,
        40.0,
    ]

    assert features[
        (
            "node-5.cartservice-0",
            "cpu_usage",
        )
    ]["n"] == 3

    print("\n========================================")
    print("TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    main()