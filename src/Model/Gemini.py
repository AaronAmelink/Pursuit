from google import genai
import os



class Gemini:
    def __init__(self):
        API_KEY = os.getenv("GEM_KEY")
        
        if not API_KEY:
            raise ValueError("API key is missing! Set the GEM_KEY environment variable with a valid API key.")
        self.client = genai.Client(api_key=API_KEY)
        self.model = "gemini-2.0-flash"
        self.key_set = API_KEY is not None
    
    def generate_content(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text