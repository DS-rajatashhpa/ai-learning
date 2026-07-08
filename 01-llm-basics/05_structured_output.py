"""
CONCEPT: Structured Output — Getting JSON Instead of Prose

In production, you never want free-form text from an LLM.
You want structured data your code can parse and use.

This is critical for RAG systems, agents, and APIs.
We use temperature=0 — structured extraction must be deterministic.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM = """
You are a crop data extractor.
Always respond with valid JSON matching this shape exactly:
{
  "crop_name": string,
  "weekly_consumption_kg": number,
  "category": "leafy" | "fruiting" | "herb",
  "grows_in_summer": boolean
}
Respond with JSON only. No explanation.
"""

crops_text = [
    "Tomato is used daily in every sabzi and dal. A family of 6 in Gurgaon needs about 3.5kg per week. It's a fruiting vegetable that struggles above 40 degrees.",
    "Coriander is a herb used as garnish on every dish. Around 200g per week is enough. It cannot survive the Gurgaon summer heat — it bolts immediately.",
    "Spinach is a leafy green, about 1kg per week, cooked as sabzi 3 times a week. It thrives in winter but dies in summer.",
]

for text in crops_text:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    data = json.loads(response.choices[0].message.content)
    print(json.dumps(data, indent=2))
    print("-" * 40)
