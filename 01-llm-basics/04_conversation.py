"""
CONCEPT: Stateless vs Stateful — How Memory Works

LLMs are stateless by default.
Each API call has zero memory of previous calls.

To give it memory, you pass the full conversation history yourself.
Every message = appended to the list = model sees everything.

This is called the "messages array" pattern — OpenAI, Gemini, Claude all use it.

Watch how the model "remembers" only because WE are keeping the history.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction="You are Jarvis, an AI assistant for an aeroponics farm. Be concise."
)

chat = model.start_chat(history=[])

questions = [
    "My farm is in Gurgaon. I grow tomatoes.",
    "What temperature should I maintain?",
    "What about in summer? It gets to 45 degrees here.",
]

for question in questions:
    print(f"USER: {question}")
    response = chat.send_message(question)
    print(f"JARVIS: {response.text.strip()}")
    print(f"[History length: {len(chat.history)} messages]")
    print("-" * 60)
