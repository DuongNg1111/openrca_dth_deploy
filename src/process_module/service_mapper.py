import re


def normalize_service_name(name: str) -> str | None:
    """
    Normalize a raw service name into a logical service name.

    Examples
    --------
    node-5.cartservice-0 -> cartservice
    node-5.frontend-0 -> frontend
    node-5.adservice-2 -> adservice

    cartservice-1 -> cartservice
    currencyservice-2 -> currencyservice

    frontend2 -> frontend
    adservice2 -> adservice

    adservice-grpc -> adservice
    adservice-http -> adservice

    adservice.ts: -> adservice
    adservice2.ts: -> adservice
    """

    # ==================================================
    # Validate input
    # ==================================================

    if not isinstance(name, str):
        return None

    name = name.strip().lower()

    if not name:
        return None

    # ==================================================
    # Remove node prefix
    # ==================================================
    #
    # node-5.cartservice-0 -> cartservice-0
    # node-5.frontend-0    -> frontend-0
    #
    # ==================================================

    name = re.sub(
        r"^node-\d+\.",
        "",
        name,
    )

    # ==================================================
    # Remove .ts / colon suffix
    # ==================================================
    #
    # adservice.ts:  -> adservice
    # adservice2.ts: -> adservice2
    # adservice.ts   -> adservice
    # adservice:     -> adservice
    #
    # ==================================================

    name = re.sub(
        r"\.ts:?$",
        "",
        name,
    )

    name = re.sub(
        r":$",
        "",
        name,
    )

    # ==================================================
    # Remove protocol suffix
    # ==================================================
    #
    # adservice-grpc -> adservice
    # adservice-http -> adservice
    #
    # ==================================================

    name = re.sub(
        r"-(grpc|http)$",
        "",
        name,
    )

    # ==================================================
    # Remove instance number with hyphen
    # ==================================================
    #
    # cartservice-1 -> cartservice
    # frontend-0    -> frontend
    #
    # ==================================================

    name = re.sub(
        r"-\d+$",
        "",
        name,
    )

    # ==================================================
    # Remove trailing number
    # ==================================================
    #
    # frontend2  -> frontend
    # adservice2 -> adservice
    #
    # ==================================================

    name = re.sub(
        r"\d+$",
        "",
        name,
    )

    # ==================================================
    # Final cleanup
    # ==================================================

    name = name.strip(" .:-_")

    if not name:
        return None

    return name