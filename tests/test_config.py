import pytest

from src.config import load_config
from src.process_module.agents.base_agent import BaseAgent


def test_yaml_llm_fields_survive_environment_overlay(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
system: Market
llm:
  source: Gemini
  model: yaml-model
  api_key_env: OPENRCA_TEST_GEMINI_KEY
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("OPENRCA_TEST_GEMINI_KEY", "placeholder-test-key")
    monkeypatch.setenv("GEMINI_MODEL", "")

    config = load_config(config_path)

    assert config["llm"]["source"] == "Gemini"
    assert config["llm"]["model"] == "yaml-model"
    assert config["llm"]["api_key_env"] == "OPENRCA_TEST_GEMINI_KEY"
    assert config["llm"]["api_key"] == "placeholder-test-key"


def test_environment_model_overrides_yaml(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n  source: Gemini\n  model: yaml-model\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GEMINI_MODEL", "environment-model")

    config = load_config(config_path)

    assert config["llm"]["source"] == "Gemini"
    assert config["llm"]["model"] == "environment-model"
    assert config["example_query"]


def test_explicit_missing_config_fails_instead_of_using_defaults(tmp_path):
    missing = tmp_path / "typoed-config.yaml"

    with pytest.raises(FileNotFoundError, match="Explicit configuration file not found"):
        load_config(missing)


def test_agent_uses_the_runtime_config_passed_by_full_pipeline(monkeypatch):
    clients = []
    monkeypatch.setattr(
        "src.process_module.agents.base_agent.genai.Client",
        lambda **kwargs: clients.append(kwargs) or object(),
    )
    runtime_config = {
        "llm": {
            "source": "Gemini",
            "model": "review-model",
            "api_key_env": "REVIEW_KEY",
            "api_key": "test-placeholder",
        }
    }

    agent = BaseAgent("Review Agent", config=runtime_config)

    assert agent.config is runtime_config
    assert agent.model_name == "review-model"
    assert clients == [{"api_key": "test-placeholder"}]
