from dotenv import load_dotenv
import os

def get_gemini_api_key():
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    return API_KEY