from dotenv import load_dotenv
load_dotenv()

from google import genai

client = genai.Client()

print("Danh sách các model khả dụng:")
print("-" * 50)
for model in client.models.list():
    # In ra tên model (ví dụ: models/gemini-2.5-flash hoặc tuỳ phiên bản)
    print(f"- {model.name}")