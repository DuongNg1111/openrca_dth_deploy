from src.jira.receive_query import receive_query
from src.input_module.validate_query import validate_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata
from src.process_module.preprocess import preprocess
from src.process_module.link_telemetry import build_service_links
from src.process_module.evidence_builder import build_investigation_context
from src.process_module.service_selector import select_services


def main():

    # -----------------------------------------
    # Step 1-7
    # -----------------------------------------

    issue_key = input("Issue Key: ")

    raw_query = receive_query(issue_key)

    validated = validate_query(raw_query)

    if not validated.is_valid:
        print(validated.errors)
        return

    parsed_query = parse_query(raw_query)

    config = {
        "system": "Market",
        "data_root": "D:/"
    }

    data_source = connect_data_source(
        parsed_query,
        config,
    )

    metadata = load_metadata(
        data_source,
        parsed_query,
    )

    telemetry = preprocess(
        metadata,
        parsed_query,
    )

    # -----------------------------------------
    # Step 8
    # -----------------------------------------

    service_links = build_service_links(
        telemetry
    )

    contexts = build_investigation_context(
        telemetry,
        service_links,
        parsed_query,
    )

    # -----------------------------------------
    # Step 9
    # -----------------------------------------

    selected = select_services(
    parsed_query,
    contexts,
    )

    print("\n========================================")
    print("SELECTED SERVICES")
    print("========================================")

    print("Affected System :", parsed_query.affected_system)
    print("Keywords        :", parsed_query.keywords)

    print()

    print("Selected Contexts :", len(selected))

    for service in selected.values():

        print("- Service :", service.service)


if __name__ == "__main__":
    main()