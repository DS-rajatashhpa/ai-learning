# AI Learning

A collection of projects built while learning AI engineering concepts from the ground up.

## Learning Path

Each folder is a standalone project that teaches one concept by building something real.

| # | Project | Core Concept |
|---|---|---|
| 01 | `llm-basics` | Calling LLMs, tokens, prompts, system vs user |
| 02 | `prompt-engineering` | Structured outputs, few-shot, chain-of-thought |
| 03 | `rag-from-scratch` | Chunking, embeddings, vector search, retrieval |
| 04 | `vector-databases` | FAISS vs ChromaDB vs Pinecone — when and why |
| 05 | `agents-and-tools` | Tool calling, ReAct pattern, function use |
| 06 | `langgraph` | Stateful agents, multi-node graphs, human-in-loop |
| 07 | `fine-tuning` | LoRA, PEFT, when to fine-tune vs RAG |
| 08 | `llmops` | MLflow, LangSmith, evaluation, RAGAS |
| — | `agrirobo-jarvis` | Flagship project — AI brain for AgriRobo |

## Stack

- Python 3.11+
- Claude API (Anthropic)
- LangChain / LangGraph
- ChromaDB → Pinecone
- Flask / FastAPI
- MLflow, LangSmith

## Rule

Every project must run end-to-end before moving to the next.
