import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GeminiAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key for Gemini is not set. Please set GEMINI_API_KEY environment variable or pass api_key.")
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def generate_content(self, prompt_text):
        import json
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": self.api_key
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt_text
                        }
                    ]
                }
            ]
        }
        print("Отправляем запрос к Gemini API:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        response = requests.post(self.url, headers=headers, params=params, json=data)
        print(f"Ответ от Gemini API: {response.status_code}")
        print(response.text)
        response.raise_for_status()
        return response.json()
