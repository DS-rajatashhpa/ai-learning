# 03 — RAG From Scratch

Build a complete RAG pipeline without any frameworks — just Python, ChromaDB, and Groq.

## Setup

```bash
cd 03-rag-from-scratch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# paste your GROQ_API_KEY
```

## Run in order

```bash
python3 01_what_is_embedding.py    # understand what a vector is
python3 02_chunk_documents.py      # split document into pieces
python3 03_build_vector_store.py   # embed + store in ChromaDB (run once)
python3 04_retrieve.py             # search by meaning
python3 05_full_rag.py             # complete pipeline: question → answer with sources
```

## The Pipeline

```
data/knowledge_base.md
  → chunk into sections
  → embed each chunk (all-MiniLM-L6-v2, 384 dimensions)
  → store in ChromaDB (persists to ./chroma_db)

User question
  → embed question (same model)
  → find top-3 similar chunks
  → build prompt with chunks as context
  → Groq/LLaMA generates grounded answer
  → return answer with source section cited
```

## Why no LangChain?

LangChain wraps exactly this code. Once you understand the raw pipeline,
using LangChain is just importing the pieces you already understand.
