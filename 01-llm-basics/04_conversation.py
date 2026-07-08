"""
CONCEPT: Stateless vs Stateful — How Memory Works

LLMs are stateless by default.
Each API call has zero memory of previous calls.

To give it memory, you pass the full conversation history yourself.
Every message = appended to the list = model sees everything.

Watch how the model "remembers" only because WE are keeping the history.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM = "You are Jarvis, an AI assistant for an aeroponics farm. Be concise."

history = [{"role": "system", "content": SYSTEM}]

questions = [
    "My farm is in Gurgaon. I grow tomatoes.",
    "What temperature should I maintain?",
    "What about in summer? It gets to 45 degrees here.",
]

for question in questions:
    history.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history
    )

    answer = response.choices[0].message.content
    history.append({"role": "assistant", "content": answer})

    print(f"USER   : {question}")
    print(f"JARVIS : {answer.strip()}")
    print(f"[History length: {len(history)} messages]")
    print("-" * 60)
