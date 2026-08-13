from google import genai

from src.config import load_config


class BaseAgent:

    def __init__(self, agent_name: str, config=None):
        self.name = agent_name

        # Load centralized configuration
        self.config = config if config is not None else load_config()

        llm_cfg = self.config.get("llm", {})

        # Gemini configuration
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get(
            "model",
            "gemini-3.5-flash"
        )

        # Initialize Gemini client
        if api_key:
            self.client = genai.Client(
                api_key=api_key
            )
        else:
            self.client = genai.Client()
