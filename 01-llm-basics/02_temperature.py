"""
CONCEPT: Temperature

Temperature controls how "random" or "creative" the output is.

  0.0 = deterministic — same input always gives same output
  1.0 = creative — output varies every run
  2.0 = chaotic — often incoherent

Rule of thumb:
  - Factual tasks (data extraction, classification) → temperature 0
  - Creative tasks (writing, brainstorming)         → temperature 0.7-1.0
  - For RAG and agents in production                → always 0 (predictable)
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = "Give me a creative name for an AI assistant that manages a farm."

temperatures = [0.0, 0.5, 1.0, 1.5]

for temp in temperatures:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT}],
        temperature=temp
    )
    print(f"Temperature {temp} → {response.choices[0].message.content.strip()}")
    print("-" * 60)
