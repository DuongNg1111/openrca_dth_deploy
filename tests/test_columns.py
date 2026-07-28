from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata
from src.jira.receive_query import receive_query
from src.input_module.query_parser import parse_query


def main():

    raw = receive_query("DEV-112")

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


    print("\n===== LOG =====")

    for file in metadata.log.files:

        print("\nFILE:", file.name)

        import pandas as pd

        df = pd.read_csv(file)

        print(df.columns.tolist())

        print(df.head(2))


    print("\n===== TRACE =====")

    for file in metadata.trace.files:

        print("\nFILE:", file.name)

        import pandas as pd

        df = pd.read_csv(file)

        print(df.columns.tolist())

        print(df.head(2))


    print("\n===== METRIC SERVICE =====")

    file = [
        f for f in metadata.metric.files
        if "service" in f.name
    ][0]


    import pandas as pd

    df = pd.read_csv(file)

    print(df.columns.tolist())

    print(df.head(2))


if __name__ == "__main__":
    main()