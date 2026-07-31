from src.process_module.service_mapper import normalize_service_name



def _init_service_record():
    """
    Initialize service relationship.
    """

    return {
        "metrics": set(),
        "logs": set(),
        "traces": set()
    }



def build_service_links(telemetry):
    """
    STEP 8.2

    Link metrics, logs and traces
    by normalized service name.

    This step only builds index.
    It does NOT merge dataframe.

    Return:

    {
        "adservice": {
            "metrics": [
                "metric_service"
            ],
            "logs": [
                "log_proxy"
            ],
            "traces": [
                "trace_span"
            ]
        }
    }
    """

    service_links = {}



    # =================================
    # 1. Metrics
    # =================================

    print("\n==============================")
    print("DEBUG METRICS")

    for name, df in telemetry.metrics.items():

        print("==============================")
        print("METRIC:", name)
        print("COLUMNS:", df.columns.tolist())

        if "service" not in df.columns:
            print(
                "SKIPPED:",
                name,
                "because no service column"
            )
            continue

        print("PROCESSING:", name)

        services = (
            df["service"]
            .dropna()
            .unique()
        )

        print(
            "FOUND SERVICES:",
            len(services)
        )

        for service in services:

            normalized = normalize_service_name(
                service
            )

            print(
                "RAW SERVICE:",
                service,
                "=> NORMALIZED:",
                normalized
            )

            if normalized is None:
                continue

            service_links.setdefault(
                normalized,
                _init_service_record()
            )

            service_links[normalized]["metrics"].add(
                name
            )

    print("\n==============================")
    print("METRIC SERVICE LINKS RESULT")

    for service, links in service_links.items():
        print(
            service,
            "=>",
            links["metrics"]
        )
    # =================================
    # 2. Logs
    # =================================

    for name, df in telemetry.logs.items():

        if "cmdb_id" not in df.columns:
            continue


        services = (
            df["cmdb_id"]
            .dropna()
            .unique()
        )


        for service in services:

            normalized = normalize_service_name(
                service
            )


            if normalized is None:
                continue


            service_links.setdefault(
                normalized,
                _init_service_record()
            )


            service_links[normalized]["logs"].add(
                name
            )



    # =================================
    # 3. Traces
    # =================================

    for name, df in telemetry.traces.items():

        if "cmdb_id" not in df.columns:
            continue


        services = (
            df["cmdb_id"]
            .dropna()
            .unique()
        )


        for service in services:

            normalized = normalize_service_name(
                service
            )


            if normalized is None:
                continue


            service_links.setdefault(
                normalized,
                _init_service_record()
            )


            service_links[normalized]["traces"].add(
                name
            )



    # =================================
    # Convert set -> list
    # =================================

    for service, relation in service_links.items():

        relation["metrics"] = sorted(
            list(relation["metrics"])
        )

        relation["logs"] = sorted(
            list(relation["logs"])
        )

        relation["traces"] = sorted(
            list(relation["traces"])
        )



    return service_links