"""
CONCEPT: Full RAG Pipeline

Putting it all together:
  User question
    → embed question
    → retrieve top-k chunks from vector DB
    → build prompt with retrieved chunks
    → LLM generates grounded answer
    → return answer WITH source citations

This is the complete pattern used in:
  - Masin's contract analysis system
  - ChatGPT with plugins
  - Enterprise document Q&A systems
  - Every "chat with your PDF" product

The LLM never hallucinates from memory — it can only use what we give it.
"""

import os
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("farm_knowledge")


def retrieve(question: str, n_results: int = 3) -> list[dict]:
    query_embedding = embedder.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n_results)
    chunks = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": doc,
            "section": meta["section"],
            "similarity": round(1 - distance, 3)
        })
    return chunks


def generate(question: str, chunks: list[dict]) -> str:
    context = "\n\n---\n\n".join([
        f"[Source: {c['section']}]\n{c['text']}" for c in chunks
    ])

    prompt = f"""You are a farm planning assistant for AgriRobo.
Answer the question using ONLY the provided context.
If the answer is not in the context, say "I don't have that information."
Always mention which section your answer comes from.

CONTEXT:
{context}

QUESTION: {question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content


def ask(question: str):
    print(f"\nQUESTION: {question}")
    print("-" * 60)

    chunks = retrieve(question)
    print(f"Retrieved {len(chunks)} chunks:")
    for c in chunks:
        print(f"  • [{c['section']}] similarity={c['similarity']}")

    answer = generate(question, chunks)
    print(f"\nANSWER:\n{answer}")
    print("=" * 60)


# Test the full pipeline
ask("How many tomato towers does a family of 6 need?")
ask("What happens to coriander in summer?")
ask("What EC level should I maintain for lettuce?")
