from google import genai
import os

API_KEY = os.getenv("GEM_KEY")


class Gemini:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)
        self.model = "gemini-2.0-flash"
        self.key_set = API_KEY is not None
    
    def generate_content(self, prompt: str) -> str:

        response = self.client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text
    
