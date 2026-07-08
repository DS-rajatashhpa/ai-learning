"""
CONCEPT: Vector Store — Storing Embeddings for Search

After chunking, we embed each chunk and store it in a vector database.
ChromaDB is a local vector DB — no server needed, persists to disk.

What the vector store holds for each chunk:
  - id        : unique identifier
  - document  : the original text
  - embedding : the vector (stored internally)
  - metadata  : anything extra (source file, page number, section name)

After this script, you have a searchable knowledge base on disk.
"""

import chromadb
from sentence_transformers import SentenceTransformer

# --- Load and chunk the knowledge base ---
with open("data/knowledge_base.md", "r") as f:
    document = f.read()

sections = document.split("\n## ")
chunks = []
for section in sections:
    if section.strip():
        title_line = section.split("\n")[0].strip("# ").strip()
        chunks.append({
            "text": section.strip(),
            "section": title_line
        })

print(f"Loaded {len(chunks)} chunks from knowledge base")

# --- Embed chunks ---
print("Embedding chunks...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
texts = [c["text"] for c in chunks]
embeddings = embedder.encode(texts).tolist()
print(f"Each chunk embedded to {len(embeddings[0])} dimensions")

# --- Store in ChromaDB ---
client = chromadb.PersistentClient(path="./chroma_db")

# Delete existing collection if re-running
try:
    client.delete_collection("farm_knowledge")
except:
    pass

collection = client.create_collection("farm_knowledge")

collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=texts,
    embeddings=embeddings,
    metadatas=[{"section": c["section"]} for c in chunks]
)

print(f"\nStored {collection.count()} chunks in ChromaDB at ./chroma_db")
print("\nChunks stored:")
for i, chunk in enumerate(chunks):
    print(f"  chunk_{i}: [{chunk['section']}] ({len(chunk['text'])} chars)")
