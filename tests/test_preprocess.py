from src.jira.receive_query import receive_query
from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata
from src.process_module.preprocess import preprocess


def main():

    issue_key = input("Enter Jira Issue Key: ")

    raw_query = receive_query(issue_key)

    validated = validate_query(raw_query)

    if not validated.is_valid:
        print(validated.errors)
        return

    parsed_query = parse_query(raw_query)

    config = {
        "system": "Market",
        "data_root": "data",
    }

    dataset_path = connect_data_source(
        parsed_query,
        config,
    )

    metadata = load_metadata(
        dataset_path,
        parsed_query,
    )

    print("\n" + "=" * 50)
    print("STEP 7 - DATA PREPROCESSING")
    print("=" * 50)

    telemetry = preprocess(metadata)

    print("\n========== SUMMARY ==========")

    print("\nMetrics")
    for name, df in telemetry.metrics.items():
        print(f"{name}: {df.shape}")

    print("\nLogs")
    for name, df in telemetry.logs.items():
        print(f"{name}: {df.shape}")

    print("\nTraces")
    for name, df in telemetry.traces.items():
        print(f"{name}: {df.shape}")

    print("\nPipeline STEP 1-7 completed.")


if __name__ == "__main__":
    main()