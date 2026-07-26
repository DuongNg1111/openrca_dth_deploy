from src.process_module.service_mapper import normalize_service_name


def main():

    samples = [
        "adservice-grpc",
        "adservice-1",
        "frontend-0",
        "currencyservice-1",
    ]


    print("==============================")
    print(" SERVICE NORMALIZATION TEST ")
    print("==============================")


    for s in samples:

        print(
            f"{s:<25} -> {normalize_service_name(s)}"
        )


if __name__ == "__main__":
    main()