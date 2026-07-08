"""
CONCEPT: Your first LLM call.

An LLM is just a function — text in, text out.
This script shows you the raw anatomy of every LLM call you will ever make.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "What is a tomato — in exactly 2 sentences."}
    ]
)

print("=" * 50)
print("RESPONSE TEXT:")
print(response.choices[0].message.content)
print("=" * 50)
print("TOKEN USAGE:")
print(f"  Input tokens  : {response.usage.prompt_tokens}")
print(f"  Output tokens : {response.usage.completion_tokens}")
print(f"  Total tokens  : {response.usage.total_tokens}")
print("=" * 50)
