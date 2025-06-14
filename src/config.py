"""
Configuration loader and shared constants for the Voice Assistant.
Loads the OpenAI API key from environment variables using dotenv.
"""

import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set")
SAMPLE_RATE: int = 24000
CHUNK_SIZE: int = 1024
CHANNELS: int = 1
