from google import genai
from src.config import load_config

class BaseAgent: # hoặc tên Agent tương ứng (MetricAgent, LogAgent, TraceAgent, ReasoningAgent)
    def __init__(self, agent_name: str):
        self.name = agent_name

class BaseAgent:

    def __init__(self, agent_name: str):
        self.name = agent_name

        # Load cấu hình tập trung
        self.config = load_config()
        llm_cfg = self.config.get("llm", {})

        # Lấy API key và model từ config
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get("model")

        # Khởi tạo Gemini client
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()