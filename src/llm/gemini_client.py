from google import genai
from google.genai import types
import json
import re
from src.config import load_config


class GeminiClient:

    def __init__(self):

        config = load_config()

        llm_config = config.get("llm", {})

        self.model = llm_config.get(
            "model",
            "gemini-3.5-flash"
        )

        api_key = llm_config.get("api_key")

        self.client = genai.Client(
            api_key=api_key
        )

    def generate(self, prompt):

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )

        text = response.text.strip()

        print("\n========== GEMINI RESPONSE ==========")
        print(text)
        print("=====================================\n")

        # thử parse trực tiếp
        try:
            json.loads(text)
            return text

        except json.JSONDecodeError:

            print("Gemini trả JSON lỗi -> đang tự làm sạch...")

            # lấy từ dấu { đầu tiên đến } cuối cùng
            m = re.search(r"\{.*\}", text, re.DOTALL)

            if m:
                cleaned = m.group(0)

                try:
                    json.loads(cleaned)
                    print("Đã sửa JSON thành công.")
                    return cleaned

                except json.JSONDecodeError as e:
                    print("JSON vẫn lỗi:")
                    print(e)
                    print(cleaned)
                    raise

            raise