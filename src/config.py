# config.py
import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
MODEL = os.getenv("MODEL")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL")