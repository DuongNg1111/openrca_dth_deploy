from src.jira.receive_query import receive_query
from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source


def main():

    print("\n==============================")
    print(" STEP 1: RECEIVE USER QUERY ")
    print("==============================")

    issue_key = input("Enter Jira Issue Key: ")

    raw_query = receive_query(issue_key)

    print("\nRAW QUERY:")
    print(raw_query)



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
    

    print("\nPARSED QUERY:")
    print(parsed_query)



    print("\n==============================")
    print(" STEP 4-5: LOAD TELEMETRY + CONNECT DATA SOURCE ")
    print("==============================")


    config = {
    "system": "Market",
    "data_root": "data"
}


    data_source = connect_data_source(
    parsed_query,
    config
)
    print("\nTELEMETRY RESULT:")

    print(data_source)



    print("\n==============================")
    print(" PIPELINE STEP 1-5 COMPLETED ")
    print("==============================")


if __name__ == "__main__":
    main()