from google import genai
from dotenv import load_dotenv
import logging

load_dotenv()

class GeminiAIService:
    client = None
    model = "gemini-2.5-flash"
    def __init__(self):
        try:
            if not self.client:
                self.client = genai.Client()
        except Exception as e:
            logging.error(f"Error when initializing Gemini client: {e}")
            raise e

    async def get_response(self, prompt: str):
        if not self.client:
            raise Exception('Please initialize GeminiAIService first')
        response_text = ""
        logging.info('Calling Gemini AI')
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt
        )
        for chunk in response:
            response_text += chunk.text
        logging.info('Completed Gemini AI call')
        return response_text