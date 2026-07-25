from src.jira.receive_query import receive_query
from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata
from dataclasses import asdict


def main():

    print("\n==============================")
    print(" STEP 1: RECEIVE USER QUERY ")
    print("==============================")

    issue_key = input("Enter Jira Issue Key: ")

    raw_query = receive_query(issue_key)

    print("\nRAW QUERY:")
    for key, value in asdict(raw_query).items():
        print(f"{key:<25}: {value}")



    print("\n==============================")
    print(" STEP 2: VALIDATE QUERY ")
    print("==============================")

    validated_result = validate_query(raw_query)


    if not validated_result.is_valid:
        print("Invalid query:")
        print(validated_result.errors)
        return

    print("\nVALIDATED QUERY:")
    print(validated_result)


    print("\n==============================")
    print(" STEP 3: PARSE QUERY ")
    print("==============================")

    parsed_query = parse_query(raw_query)
    

    for key, value in asdict(parsed_query).items():
        print(f"{key:<25}: {value}")

    print("\n==============================")
    print(" STEP 4-5: LOAD TELEMETRY + CONNECT DATA SOURCE ")
    print("==============================")

    config = {
        "system": "Market",
        "data_root": "data",
}

    data_source = connect_data_source(
        parsed_query,
        config
)
    print("\nTELEMETRY RESULT:")

    print(data_source)

    print("\n==============================")
    print(" STEP 6: LOAD TELEMETRY DATA")
    print("==============================")

    metadata = load_metadata(
        data_source,
        parsed_query,
    )
    print("\n")
    print("Date Folder :", metadata.date)
    print("Metric Files:", len(metadata.metric.files))
    print("Log Files   :", len(metadata.log.files))
    print("Trace Files :", len(metadata.trace.files))
    print(
        "Total Files :",
        len(metadata.metric.files)
        + len(metadata.log.files)
        + len(metadata.trace.files)
    )

    print("\n==============================")
    print(" PIPELINE STEP 1-6 COMPLETED ")
    print("==============================")


if __name__ == "__main__":
    main()