from src.process_module.link_telemetry import build_service_links
from src.process_module.preprocess import preprocess
from src.process_module.metadata_loader import load_metadata
from src.input_module.parse_query import parse_query
from src.schemas import RawQuery


def test_service_links_metric():


    # ==========================
    # 1. Fake query
    # ==========================

    raw_query = RawQuery(
        issue_key="DEV-125",
        incident_description="can not find product AAA",
        environment="Cloud B",
        affected_system="Search Products",
        incident_time="2022-03-20 10:10:00"
    )


    parsed_query = parse_query(
        raw_query
    )


    # ==========================
    # 2. Load metadata
    # ==========================

    metadata = load_metadata(
        "/home/ubuntu/Market/cloudbed-2/telemetry",
        parsed_query
    )


    # ==========================
    # 3. Preprocess
    # ==========================

    telemetry = preprocess(
        metadata,
        parsed_query
    )


    # ==========================
    # 4. Build links
    # ==========================

    links = build_service_links(
        telemetry
    )


    # ==========================
    # 5. Check
    # ==========================

    print("\n======================")
    for service, data in links.items():
        print(
            service,
            "=>",
            data["metrics"]
        )


    assert (
        "productcatalogservice"
        in links
    )


    assert (
        "metric_service"
        in links["productcatalogservice"]["metrics"]
    )