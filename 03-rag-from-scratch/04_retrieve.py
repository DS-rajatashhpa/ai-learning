"""
CONCEPT: Retrieval — Finding Relevant Chunks by Meaning

Given a user question, find the most semantically similar chunks.
This is the R in RAG — Retrieval Augmented Generation.

The retriever:
  1. Embeds the question (same model used during ingestion)
  2. Computes similarity between question vector and all chunk vectors
  3. Returns top-k most similar chunks

Key insight: the question and the answer use DIFFERENT words,
but their embeddings are CLOSE in vector space.
"""

import chromadb
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("farm_knowledge")

queries = [
    "How many towers do I need for tomatoes?",
    "What crops can I grow in summer in Gurgaon?",
    "What is the correct pH for my hydroponic system?",
    "How do I manage coriander so it keeps growing?",
]

for query in queries:
    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )

    print(f"QUERY: {query}")
    print(f"TOP MATCHES:")
    for i, (doc, meta, distance) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        similarity = 1 - distance
        print(f"  [{i+1}] Section: {meta['section']} | Similarity: {similarity:.3f}")
        print(f"       {doc[:150]}...")
    print("-" * 70)
