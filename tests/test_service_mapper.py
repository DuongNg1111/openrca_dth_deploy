from src.process_module.service_mapper import normalize_service_name


def main():

    print("\n========================================")
    print("TEST SERVICE MAPPER")
    print("========================================")

    test_cases = [
        "node-5.cartservice-0",
        "node-5.frontend-0",
        "node-5.adservice-2",
        "node-6.frontend2-0",
        "cartservice-1",
        "currencyservice-2",
        "frontend2",
        "adservice-grpc",
        "adservice-http",
        "paymentservice",
        "checkoutservice",
    ]

    expected = [
        "cartservice",
        "frontend",
        "adservice",
        "frontend",
        "cartservice",
        "currencyservice",
        "frontend",
        "adservice",
        "adservice",
        "paymentservice",
        "checkoutservice",
    ]

    print("\nRESULTS")
    print("----------------------------------------")

    for raw, expected_value in zip(test_cases, expected):

        result = normalize_service_name(raw)

        print(
            f"{raw:<40} -> {result}"
        )

        assert result == expected_value, (
            f"FAILED: {raw} -> {result}, "
            f"expected {expected_value}"
        )

    print("\n========================================")
    print("TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    main()