import logging
import os
from dotenv import load_dotenv
import google.generativeai as genai

def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger(__name__)

def configure_gemini():
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is missing in environment variables.")
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai