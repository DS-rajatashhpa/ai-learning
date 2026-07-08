"""
CONCEPT: System Prompt vs User Prompt

Every LLM call has two layers:

  System prompt  →  WHO the model is. Permanent. User never sees this.
  User prompt    →  WHAT is being asked right now.

Think of it like:
  System = middleware that runs before every request
  User   = the actual request body

Same user question. Different system prompt. Completely different answer.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

USER_QUESTION = "Should I be worried?"

personas = [
    {
        "name": "Doctor",
        "system": "You are a medical doctor. Be clinical and precise."
    },
    {
        "name": "Legal Advisor",
        "system": "You are a construction contract lawyer. Think in terms of liability and risk."
    },
    {
        "name": "Farmer",
        "system": "You are an experienced farmer in Gurgaon. Think about crops, weather, and seasons."
    },
]

for persona in personas:
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=persona["system"]
    )
    response = model.generate_content(USER_QUESTION)
    print(f"[{persona['name']}]")
    print(f"System: {persona['system']}")
    print(f"Answer: {response.text.strip()}")
    print("=" * 60)
