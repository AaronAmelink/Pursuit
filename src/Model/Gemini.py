from google import genai
from dotenv import load_dotenv
import os

class Gemini:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()

        # Retrieve the API key from the environment
        API_KEY = os.getenv("GEM_KEY")


        if not API_KEY:
            raise ValueError("API key is missing! Set the GEM_KEY environment variable in the .env file.")
        
        # Initialize the genai client with the API key
        self.client = genai.Client(api_key=API_KEY)
        self.model = "gemini-2.0-flash"
        self.job_description = ""
    
    def generate_content(self, prompt: str) -> str:
        system_prompt = (
            "You are a helpful assistant, designed to assist users in learning about job opportunities. "
            "Your task is to provide relevant information and answer questions based on the user's questions and the job description provided. "
            "You should be informative, concise, and helpful. Job description: "
        )
        response = self.client.models.generate_content(
            model=self.model, contents=system_prompt + self.job_description + prompt
        )
        return response.text