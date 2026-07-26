import re


def normalize_service_name(name: str) -> str | None:
    """
    Normalize service identity.

    Examples:
        adservice-grpc -> adservice
        adservice-http -> adservice
        adservice-1    -> adservice
        frontend-0     -> frontend
        frontend2      -> frontend
        adservice2     -> adservice
    """

    if not isinstance(name, str):
        return None

    name = name.lower()

    # Remove protocol suffix
    name = re.sub(
        r"-(grpc|http)$",
        "",
        name
    )

    # Remove instance number with hyphen
    name = re.sub(
        r"-\d+$",
        "",
        name
    )

    # Remove trailing number without hyphen
    name = re.sub(
        r"\d+$",
        "",
        name
    )

    return name