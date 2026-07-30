"""Minimal local connectivity check for the Gemini API."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY is not set in backend/.env.")

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Reply with a short confirmation that the Gemini connection works.",
)
print(response.text)
