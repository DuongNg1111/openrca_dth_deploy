from src.process_module.service_links import build_service_links
from src.process_module.preprocess import preprocess_telemetry

# tùy project của bà tên file load/preprocess khác nhau thì chỉnh import


def test_debug_service_links():

    telemetry = preprocess_telemetry(
        data_path="/home/ubuntu/Market/cloudbed-2/telemetry",
        incident_time="2022-03-20 10:10:00"
    )

    print("\n==============================")
    print("METRIC KEYS")
    print(telemetry.metrics.keys())

    for name, df in telemetry.metrics.items():
        print("\nMETRIC:", name)
        print(df.columns.tolist())
        print(df.head())


    service_links = build_service_links(
        telemetry
    )

    print("\n==============================")
    print("SERVICE LINKS")

    for service, links in service_links.items():
        print(service)
        print("METRICS:", links["metrics"])
        print("LOGS:", links["logs"])
        print("TRACES:", links["traces"])