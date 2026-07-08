"""
CONCEPT: Prompt Templates

In production, you never hardcode prompts.
You build templates with variables — filled at runtime with real data.

This is exactly what LangChain's PromptTemplate does under the hood.
Understanding this means you understand what every AI framework is built on.

Real use cases:
  - RAG: template fills in {retrieved_chunks} + {user_question}
  - Agents: template fills in {tools_available} + {conversation_history}
  - Masin: template fills in {contract_clauses} + {dispute_question}
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(template: str, **kwargs) -> str:
    """Fill a prompt template with variables. This is PromptTemplate."""
    return template.format(**kwargs)


# --- Template 1: RAG answer template ---
RAG_TEMPLATE = """You are a contract analyst for construction disputes.
Answer the question using ONLY the provided contract clauses.
If the answer is not in the clauses, say "Not found in contract."
Always cite the clause number.

CONTRACT CLAUSES:
{retrieved_clauses}

QUESTION: {question}

Answer with citation:"""

clauses = """
Clause 14.1: The contractor shall be liable for liquidated damages of 2% of
contract value per week of delay, up to a maximum of 20%.

Clause 14.2: Liquidated damages shall not apply if delay is caused by employer
acts or force majeure events as defined in Clause 19.

Clause 19.1: Force majeure includes acts of God, war, and government actions
preventing performance for more than 30 consecutive days.
"""

prompt1 = build_prompt(
    RAG_TEMPLATE,
    retrieved_clauses=clauses,
    question="What is the maximum penalty the contractor can face for delays?"
)

prompt2 = build_prompt(
    RAG_TEMPLATE,
    retrieved_clauses=clauses,
    question="Can the contractor avoid penalties if there is a flood?"
)

for question, prompt in [
    ("Max delay penalty?", prompt1),
    ("Flood exemption?", prompt2)
]:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    print(f"Q: {question}")
    print(f"A: {response.choices[0].message.content.strip()}")
    print("-" * 60)
