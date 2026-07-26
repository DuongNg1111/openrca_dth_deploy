from pathlib import Path


def connect_data_source(parsed_query, config):
    """
    Step 5
    5.1 Connect Raw Database
    5.2 Verify Connection
    5.3 Select Data Source
    """

    system = config["system"]
    data_root = config["data_root"]

    # =========================
    # Step 5.1 Connect Raw Database
    # =========================

    environment_map = {
        "Cloud A": "cloudbed-1",
        "Cloud B": "cloudbed-2",
    }


    dataset_folder = environment_map.get(
        parsed_query.environment
    )


    if dataset_folder is None:
        raise ValueError(
            f"Unknown environment: {parsed_query.environment}"
        )


    dataset_path = (
        Path(data_root)
        / system
        / dataset_folder
        / "telemetry"
    )


    # =========================
    # Step 5.2 Verify Connection
    # =========================

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )


    # =========================
    # Step 5.3 Select Data Source
    # =========================

    print("=" * 40)
    print("DATA SOURCE")
    print("=" * 40)

    print("System      :", system)
    print("Environment :", parsed_query.environment)
    print("Dataset     :", dataset_folder)
    print("Dataset Path:", dataset_path)


    return dataset_path