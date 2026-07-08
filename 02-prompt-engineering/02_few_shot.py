"""
CONCEPT: Few-Shot Prompting

Instead of describing what you want, SHOW the model with examples.
A few input-output examples in the prompt = "few-shot."
Zero examples = "zero-shot."

Few-shot is powerful when:
  - Output format is specific and hard to describe
  - The task has a pattern the model should replicate
  - Zero-shot gives inconsistent formatting

In production RAG systems, few-shot examples are used to
control exactly how the model cites sources and structures answers.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Zero-shot: just describe the task
zero_shot_messages = [
    {
        "role": "system",
        "content": "Extract the risk level from construction contract clauses. Respond with: clause, risk_level (low/medium/high), reason."
    },
    {
        "role": "user",
        "content": "The contractor shall be liable for liquidated damages of 2% of contract value per week of delay, up to a maximum of 20%."
    }
]

# Few-shot: show examples first, then ask
few_shot_messages = [
    {
        "role": "system",
        "content": "Extract the risk level from construction contract clauses."
    },
    # Example 1
    {"role": "user", "content": "The contractor warrants all work for 12 months post-completion."},
    {"role": "assistant", "content": "CLAUSE: 12-month warranty\nRISK: medium\nREASON: Standard warranty period, but exposes contractor to defect claims for a full year."},
    # Example 2
    {"role": "user", "content": "Force majeure events shall not excuse delay beyond 30 days."},
    {"role": "assistant", "content": "CLAUSE: Force majeure cap at 30 days\nRISK: high\nREASON: 30-day cap is unusually short — events like COVID or natural disasters easily exceed this, leaving contractor liable."},
    # Now the real question
    {
        "role": "user",
        "content": "The contractor shall be liable for liquidated damages of 2% of contract value per week of delay, up to a maximum of 20%."
    }
]

response_zero = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=zero_shot_messages,
    temperature=0
)

response_few = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=few_shot_messages,
    temperature=0
)

print("ZERO-SHOT:")
print(response_zero.choices[0].message.content)
print("\n" + "=" * 60 + "\n")
print("FEW-SHOT:")
print(response_few.choices[0].message.content)
