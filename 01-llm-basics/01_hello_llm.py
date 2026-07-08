"""
CONCEPT: Your first LLM call.

An LLM is just a function — text in, text out.
This script shows you the raw anatomy of every LLM call you will ever make.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("What is a tomato — in exactly 2 sentences.")

print("=" * 50)
print("RESPONSE TEXT:")
print(response.text)
print("=" * 50)
print("TOKEN USAGE:")
print(f"  Input tokens  : {response.usage_metadata.prompt_token_count}")
print(f"  Output tokens : {response.usage_metadata.candidates_token_count}")
print(f"  Total tokens  : {response.usage_metadata.total_token_count}")
print("=" * 50)
