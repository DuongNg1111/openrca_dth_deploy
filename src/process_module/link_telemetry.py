from src.process_module.service_mapper import (
    normalize_service_name,
)


# =====================================================
# Extract Logical Service
# =====================================================

def _extract_logical_service(raw_service: str) -> str | None:
    """
    Convert a raw telemetry / CMDB service name
    into its logical service name.

    Examples
    --------
    node-5.cartservice-0
        -> cartservice

    checkoutservice-2.source.checkoutservice.cartservice
        -> checkoutservice

    checkoutservice-2.destination.frontend.checkoutservice
        -> checkoutservice

    frontend-0.source.frontend.cartservice
        -> frontend

    currencyservice-2.destination.frontend.currencyservice
        -> currencyservice
    """

    if not isinstance(raw_service, str):
        return None

    raw_service = raw_service.strip().lower()

    if not raw_service:
        return None

    # -------------------------------------------------
    # SOURCE ENTITY
    # -------------------------------------------------
    #
    # Example:
    #
    # checkoutservice-2.source.checkoutservice.cartservice
    #
    # The service producing the telemetry is the part
    # before ".source."
    #
    # -> checkoutservice-2
    # -> checkoutservice
    #
    # -------------------------------------------------

    if ".source." in raw_service:

        source_part = raw_service.split(
            ".source.",
            1,
        )[0]

        return normalize_service_name(
            source_part
        )

    # -------------------------------------------------
    # DESTINATION ENTITY
    # -------------------------------------------------
    #
    # Example:
    #
    # checkoutservice-2.destination.frontend.checkoutservice
    #
    # Destination:
    #
    # frontend.checkoutservice
    #
    # The actual logical service is the LAST component:
    #
    # -> checkoutservice
    #
    # -------------------------------------------------

    if ".destination." in raw_service:

        destination_part = raw_service.split(
            ".destination.",
            1,
        )[1]

        parts = destination_part.split(".")

        if not parts:
            return None

        return normalize_service_name(
            parts[-1]
        )

    # -------------------------------------------------
    # NORMAL SERVICE
    # -------------------------------------------------
    #
    # Examples:
    #
    # node-5.cartservice-0
    # cartservice-1
    # frontend2
    # adservice-grpc
    #
    # -------------------------------------------------

    return normalize_service_name(
        raw_service
    )


# =====================================================
# Initialize Service Record
# =====================================================

def _init_service_record():
    """
    Initialize an empty service relationship record.

    Each service can be associated with:
        - metrics
        - logs
        - traces
    """

    return {
        "metrics": set(),
        "logs": set(),
        "traces": set(),
    }


# =====================================================
# Add Service Relation
# =====================================================

def _add_service_relation(
    service_links,
    service,
    telemetry_type,
    dataset_name,
):
    """
    Add a telemetry dataset to a logical service.
    """

    if service is None:
        return

    # -------------------------------------------------
    # Convert raw CMDB / telemetry entity
    # into logical service
    # -------------------------------------------------

    normalized = _extract_logical_service(
        service
    )

    if normalized is None:
        return

    normalized = str(
        normalized
    ).strip()

    if not normalized:
        return

    # -------------------------------------------------
    # Create service record
    # -------------------------------------------------

    service_links.setdefault(
        normalized,
        _init_service_record(),
    )

    # -------------------------------------------------
    # Add telemetry dataset
    # -------------------------------------------------

    service_links[
        normalized
    ][telemetry_type].add(
        dataset_name
    )


# =====================================================
# Build Service Links
# =====================================================

def build_service_links(telemetry):
    """
    Build service relationship index from processed
    telemetry.

    Expected telemetry structure:

        telemetry.metrics
        telemetry.logs
        telemetry.traces

    Each one should be:

        {
            "dataset_name": pandas.DataFrame
        }

    DataFrames must contain:

        cmdb_id

    Returns:

        {
            "service_name": {
                "metrics": [...],
                "logs": [...],
                "traces": [...]
            }
        }
    """

    service_links = {}

    # =================================================
    # 1. METRICS
    # =================================================

    print("\n==============================")
    print("BUILD SERVICE LINKS: METRICS")
    print("==============================")

    for name, df in telemetry.metrics.items():

        print("\nMETRIC:", name)

        if df is None:
            print(
                "SKIPPED: DataFrame is None"
            )
            continue

        if df.empty:
            print(
                "SKIPPED: DataFrame is empty"
            )
            continue

        if "cmdb_id" not in df.columns:
            print(
                "SKIPPED: cmdb_id column not found"
            )
            continue

        services = (
            df["cmdb_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        print(
            "Raw services found:",
            len(services),
        )

        for service in services:

            _add_service_relation(
                service_links=service_links,
                service=service,
                telemetry_type="metrics",
                dataset_name=name,
            )

    # =================================================
    # 2. LOGS
    # =================================================

    print("\n==============================")
    print("BUILD SERVICE LINKS: LOGS")
    print("==============================")

    for name, df in telemetry.logs.items():

        print("\nLOG:", name)

        if df is None:
            print(
                "SKIPPED: DataFrame is None"
            )
            continue

        if df.empty:
            print(
                "SKIPPED: DataFrame is empty"
            )
            continue

        if "cmdb_id" not in df.columns:
            print(
                "SKIPPED: cmdb_id column not found"
            )
            continue

        services = (
            df["cmdb_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        print(
            "Raw services found:",
            len(services),
        )

        for service in services:

            _add_service_relation(
                service_links=service_links,
                service=service,
                telemetry_type="logs",
                dataset_name=name,
            )

    # =================================================
    # 3. TRACES
    # =================================================

    print("\n==============================")
    print("BUILD SERVICE LINKS: TRACES")
    print("==============================")

    for name, df in telemetry.traces.items():

        print("\nTRACE:", name)

        if df is None:
            print(
                "SKIPPED: DataFrame is None"
            )
            continue

        if df.empty:
            print(
                "SKIPPED: DataFrame is empty"
            )
            continue

        if "cmdb_id" not in df.columns:
            print(
                "SKIPPED: cmdb_id column not found"
            )
            continue

        services = (
            df["cmdb_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        print(
            "Raw services found:",
            len(services),
        )

        for service in services:

            _add_service_relation(
                service_links=service_links,
                service=service,
                telemetry_type="traces",
                dataset_name=name,
            )

    # =================================================
    # Convert Sets -> Sorted Lists
    # =================================================

    for service, relation in service_links.items():

        relation["metrics"] = sorted(
            relation["metrics"]
        )

        relation["logs"] = sorted(
            relation["logs"]
        )

        relation["traces"] = sorted(
            relation["traces"]
        )

    # =================================================
    # Debug Output
    # =================================================

    print("\n==============================")
    print("SERVICE LINKS RESULT")
    print("==============================")

    for service, relation in sorted(
        service_links.items()
    ):

        print("\nSERVICE:", service)

        print(
            "  Metrics:",
            relation["metrics"],
        )

        print(
            "  Logs:",
            relation["logs"],
        )

        print(
            "  Traces:",
            relation["traces"],
        )

    print(
        "\nTotal logical services:",
        len(service_links),
    )

    return service_links