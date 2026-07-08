# 02 — Prompt Engineering

## Setup

```bash
cd 02-prompt-engineering
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# paste your GROQ_API_KEY
```

## Scripts

| Script | Concept |
|---|---|
| `01_chain_of_thought.py` | Think step by step → better reasoning |
| `02_few_shot.py` | Show examples → consistent output format |
| `03_prompt_template.py` | Templates with variables → foundation of every AI framework |

```bash
python3 01_chain_of_thought.py
python3 02_few_shot.py
python3 03_prompt_template.py
```

## What to take away

- Chain-of-thought: always use for multi-step reasoning tasks
- Few-shot: use when output format consistency matters
- Prompt templates: this IS what LangChain/LangGraph builds on — now you know the foundation
