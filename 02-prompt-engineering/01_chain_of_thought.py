"""
CONCEPT: Chain-of-Thought Prompting

By default, LLMs jump straight to an answer.
For complex reasoning, this causes wrong answers.

Chain-of-thought = tell the model to "think step by step" before answering.
This forces it to reason through the problem, dramatically improving accuracy.

This is critical for:
  - Legal clause analysis ("is this clause enforceable?")
  - Multi-step calculations (tower counts, yield planning)
  - Diagnosis tasks ("what is wrong with this sensor reading?")
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROBLEM = """
A family of 6 in Gurgaon needs 3.5kg of tomatoes per week.
One tomato plant yields 400g per week once fruiting.
Each tower holds 2 tomato plants.
A new batch of plants needs 75 days before first fruit.
How many towers are needed so the family always has tomatoes,
accounting for the time gap between batches?
"""

# Without chain-of-thought
response_direct = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": PROBLEM}],
    temperature=0
)

# With chain-of-thought
response_cot = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{
        "role": "user",
        "content": PROBLEM + "\n\nThink through this step by step before giving the final answer."
    }],
    temperature=0
)

print("WITHOUT chain-of-thought:")
print(response_direct.choices[0].message.content)
print("\n" + "=" * 60 + "\n")
print("WITH chain-of-thought:")
print(response_cot.choices[0].message.content)
