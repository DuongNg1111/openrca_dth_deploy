from google import genai

from src.config import load_config


class BaseAgent:

    def __init__(self, agent_name: str, config=None):
        self.name = agent_name

        # Use the full pipeline's runtime config when supplied. Reloading the default
        # here would silently ignore a custom --config model/api_key_env selection.
        self.config = load_config() if config is None else config
        llm_cfg = self.config.get("llm", {})

        # Lấy API key và model từ config
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get("model")

        # Khởi tạo Gemini client
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()
