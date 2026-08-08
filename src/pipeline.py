"""End-to-end pipeline: INPUT -> PROCESS -> OUTPUT.

Run it:  python -m src.pipeline
Works out of the box on mock telemetry and prints an OpenRCA-format result.
"""
from __future__ import annotations

import json

from src import input_module, output_module, process_module
from src.config import load_config
from src.schemas import Prediction


def run(query: str, config: dict) -> Prediction:
    """Run the three modules in sequence and return a Prediction."""
    ctx = input_module.build_input_context(query, config)
    candidates = process_module.analyze(ctx, top_k=config.get("top_k", 1))
    return output_module.build_output(candidates)


def main() -> None:
    cfg = load_config()
    # This command is the documented no-dataset quickstart. The separate
    # ``src.full_pipeline`` entry point continues to use the real-data config.
    mock_config = {**cfg, "use_mock": True}
    pred = run(mock_config["example_query"], mock_config)
    print(json.dumps(pred.to_openrca_json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
