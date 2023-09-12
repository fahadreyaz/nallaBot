import json
from dotenv import load_dotenv
import os
import requests

load_dotenv()

class OpenAi:
    def __init__(self, prompt: str):
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.api_key = os.getenv("API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        self.jsonData = {
            "model": "gpt-3.5-turbo",
            "temperature": 1,
            "top_p": 1,
            "frequency_penalty": 1,
            "presence_penalty": 1,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

    def getResponse(self):
        response = requests.post(self.api_url, headers=self.headers, json=self.jsonData)
        return json.loads(response.text)["choices"][0]["message"]["content"]
