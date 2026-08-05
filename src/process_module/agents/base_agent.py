from src.config import load_config

class BaseAgent: # hoặc tên Agent tương ứng (MetricAgent, LogAgent, TraceAgent, ReasoningAgent)
    def __init__(self, agent_name: str):
        self.name = agent_name

        # 1. Load cấu hình tập trung từ config.py
        self.config = load_config()
        llm_cfg = self.config.get("llm", {})

        # 2. Lấy api_key và model_name trực tiếp từ file cấu hình chung
        api_key = llm_cfg.get("api_key")
        self.model_name = llm_cfg.get("model")  # Bắt buộc lấy từ config, không hardcode ở đây

        # 3. Khởi tạo client Gemini
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()