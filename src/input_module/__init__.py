"""INPUT module (DEV 1): query + telemetry -> InputContext."""
from __future__ import annotations

from src.input_module import telemetry_loader
from src.input_module.query_parser import parse_query
from src.schemas import InputContext


def build_input_context(query: str, config: dict) -> InputContext:
    """Parse the NL query and load the matching telemetry slice."""
    window, hints = parse_query(query, default_date=config.get("default_date", "2021-03-25"))
    if config.get("use_mock", True):
        telemetry = telemetry_loader.load_mock(window)
    else:
        telemetry = telemetry_loader.load(config["system"], window, config["data_root"])
    return InputContext(
        raw_query=query,
        system=config.get("system", "Market"),
        time_window=window,
        components_hint=hints,
        telemetry=telemetry,
    )
