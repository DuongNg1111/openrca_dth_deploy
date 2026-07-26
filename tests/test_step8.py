from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata
from src.input_module.query_parser import parse_query
from src.jira.receive_query import receive_query

from src.process_module.preprocess import preprocess
from src.process_module.link_telemetry import build_service_links


def main():

    raw = receive_query(
        "DEV-112"
    )


    parsed = parse_query(raw)


    config = {
        "system": "Market",
        "data_root": "D:/"
    }


    path = connect_data_source(
        parsed,
        config
    )


    metadata = load_metadata(
        path,
        parsed
    )


    telemetry = preprocess(
        metadata,
        parsed
    )
    print("\nTRACE DEBUG")
    for name, df in telemetry.traces.items():
        print(name)
        print(df.columns)
        print(df.head())


    links = build_service_links(
        telemetry
    )


    print("==============================")
    print(" STEP 8.2 SERVICE LINK ")
    print("==============================")


    count = 0

    for service, relation in links.items():

        print("\nSERVICE:", service)

        print(
            "Metrics:",
            relation["metrics"]
        )

        print(
            "Logs:",
            relation["logs"]
        )

        print(
            "Traces:",
            relation["traces"]
        )


        count += 1


        if count == 10:
            break



if __name__ == "__main__":
    main()