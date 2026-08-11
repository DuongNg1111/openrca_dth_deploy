from src.config import load_config

config = load_config()

print("=" * 40)
print("CONFIG")
print("=" * 40)

print("System      :", config["system"])
print("Data Root   :", config["data_root"])
print("Use Mock    :", config["use_mock"])
# print("Default Date:", config["default_date"])
print("Top K       :", config["top_k"])

print("\nLLM")
print("Source      :", config["llm"]["source"])
print("Model       :", config["llm"]["model"])
print("API Env     :", config["llm"]["api_key_env"])