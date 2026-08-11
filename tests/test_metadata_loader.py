from src.config import load_config
from src.jira.receive_query import receive_query
from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import build_metadata_index


def main():

    issue_key = input("Enter Jira Issue Key: ")

    raw_query = receive_query(issue_key)

    validated = validate_query(raw_query)

    if not validated.is_valid:
        print(validated.errors)
        return

    parsed = parse_query(raw_query)

    config = load_config()

    dataset_path = connect_data_source(
        parsed,
        config,
    )

    metadata = build_metadata_index(
        dataset_path,
        parsed,
    )

    print("\n========== STEP 6 ==========\n")

    print("\n========== STEP 6 ==========")

    print(f"Date         : {metadata.date}")
    print(f"Total Files  : {metadata.total_files}")

    print("\nMetric")
    print(f"  Folder     : {metadata.metric.folder}")
    print(f"  File Count : {metadata.metric.count}")

    print("\nLog")
    print(f"  Folder     : {metadata.log.folder}")
    print(f"  File Count : {metadata.log.count}")

    print("\nTrace")
    print(f"  Folder     : {metadata.trace.folder}")
    print(f"  File Count : {metadata.trace.count}")

    print("\nMetric Files")
    for file in metadata.metric.files:
        print(file.name)

    print("\nLog Files")
    for file in metadata.log.files:
        print(file.name)

    print("\nTrace Files")
    for file in metadata.trace.files:
        print(file.name)


if __name__ == "__main__":
    main()