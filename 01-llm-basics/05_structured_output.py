"""
CONCEPT: Structured Output — Getting JSON Instead of Prose

In production, you never want free-form text from an LLM.
You want structured data your code can parse and use.

Two ways to get JSON:
  1. Prompt it: "respond only in JSON"
  2. Schema enforcement: tell the model the exact shape you want

This is critical for:
  - RAG systems (structured citations)
  - Agents (structured tool calls)
  - APIs (your Flask endpoint returning clean data)

We use temperature=0 here. Structured extraction = always deterministic.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    generation_config=genai.GenerationConfig(
        temperature=0,
        response_mime_type="application/json"
    ),
    system_instruction="""
    You are a crop data extractor.
    Always respond with valid JSON matching this shape exactly:
    {
      "crop_name": string,
      "weekly_consumption_kg": number,
      "category": "leafy" | "fruiting" | "herb",
      "grows_in_summer": boolean
    }
    """
)

crops_text = [
    "Tomato is used daily in every sabzi and dal. A family of 6 in Gurgaon needs about 3.5kg per week. It's a fruiting vegetable that struggles above 40 degrees.",
    "Coriander is a herb used as garnish on every dish. Around 200g per week is enough. It cannot survive the Gurgaon summer heat — it bolts immediately.",
    "Spinach is a leafy green, about 1kg per week, cooked as sabzi 3 times a week. It thrives in winter but dies in summer.",
]

for text in crops_text:
    response = model.generate_content(text)
    data = json.loads(response.text)
    print(json.dumps(data, indent=2))
    print("-" * 40)
