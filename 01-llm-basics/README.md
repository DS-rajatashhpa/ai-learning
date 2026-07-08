# 01 — LLM Basics

**One rule:** run each script, read the output, understand WHY before moving to the next.

## Setup

```bash
cd 01-llm-basics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# paste your Gemini API key into .env
```

## Scripts — Run in Order

| Script | Concept | What You See |
|---|---|---|
| `01_hello_llm.py` | First API call, token counts | Raw response + how many tokens were used |
| `02_temperature.py` | Randomness control | Same prompt, 4 different temperatures, 4 different outputs |
| `03_system_prompt.py` | System vs user prompt | Same question, 3 personas, 3 completely different answers |
| `04_conversation.py` | Stateless vs stateful | How memory works — you are the memory |
| `05_structured_output.py` | JSON output | LLM returns structured data your code can use |

```bash
python3 01_hello_llm.py
python3 02_temperature.py
python3 03_system_prompt.py
python3 04_conversation.py
python3 05_structured_output.py
```

## What You Should Be Able to Say After This

- "An LLM is stateless — memory is an illusion we create by passing history"
- "Temperature 0 for any production/extraction task — predictability matters"
- "System prompt is middleware. User prompt is the request."
- "Always get structured output in production. Never parse free text."

## Next

→ `02-prompt-engineering`
