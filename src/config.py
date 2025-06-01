"""
Configuration loader for the Voice Assistant.
Loads the OpenAI API key from environment variables using dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
