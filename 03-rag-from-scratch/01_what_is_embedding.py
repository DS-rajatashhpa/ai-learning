"""
CONCEPT: What is an Embedding?

An embedding is a sentence converted into a list of numbers (a vector)
that captures its MEANING, not its exact words.

Key property: similar meaning = similar numbers = close in vector space.

This is the foundation of all semantic search, RAG, and vector databases.
Without embeddings, you can only do keyword search (like grep).
With embeddings, you can search by MEANING.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "The penalty for delay is 1% per week",        # legal / delay
    "Late delivery incurs a 1% weekly fee",         # legal / delay — different words, same meaning
    "Liquidated damages apply after 7 days",        # legal / delay — related
    "Tomatoes need 22 degrees Celsius to grow",     # farming — completely unrelated
    "The reservoir should be changed every 10 days" # farming — unrelated
]

print("Generating embeddings...")
embeddings = model.encode(sentences)
print(f"Each sentence → vector of {len(embeddings[0])} numbers\n")

print("Sample of first sentence's vector (first 8 numbers):")
print([round(x, 4) for x in embeddings[0][:8]])
print()

print("SIMILARITY SCORES (1.0 = identical meaning, 0.0 = unrelated):")
print("-" * 60)
base = sentences[0]
base_embedding = embeddings[0].reshape(1, -1)

for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
    score = cosine_similarity(base_embedding, embedding.reshape(1, -1))[0][0]
    print(f"{score:.3f}  |  {sentence}")

print()
print("Notice: sentences 0, 1, 2 have HIGH similarity despite different words.")
print("Sentence 3 and 4 have LOW similarity — different domain entirely.")
print("This is why RAG works: it finds meaning, not just keywords.")
