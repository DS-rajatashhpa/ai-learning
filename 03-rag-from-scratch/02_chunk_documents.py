"""
CONCEPT: Chunking — Splitting Documents for RAG

You cannot embed a 500-page contract as one piece.
You must split it into smaller chunks first.

Why chunking matters:
  - Embedding models have a max input size (~512 tokens)
  - Smaller chunks = more precise retrieval
  - Too small = loses context, too large = retrieves irrelevant content

Three chunking strategies:
  1. Fixed size: split every N characters — simple, ignores meaning
  2. By separator: split on paragraphs/sections — respects document structure
  3. Sentence-aware: split on sentence boundaries — preserves readability

Overlap: chunks share N characters with neighbors so context isn't lost at boundaries.
"""

def chunk_fixed(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split by character count with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 50]


def chunk_by_paragraph(text: str) -> list[str]:
    """Split on double newlines (paragraph boundaries)."""
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if len(p.strip()) > 50]


def chunk_by_section(text: str) -> list[str]:
    """Split on ## headers — respects document structure."""
    sections = text.split("\n## ")
    chunks = []
    for section in sections:
        if section.strip():
            chunks.append("## " + section.strip() if not section.startswith("#") else section.strip())
    return chunks


with open("data/knowledge_base.md", "r") as f:
    document = f.read()

print(f"Original document: {len(document)} characters\n")

fixed_chunks = chunk_fixed(document, chunk_size=400, overlap=50)
para_chunks = chunk_by_paragraph(document)
section_chunks = chunk_by_section(document)

print(f"Fixed-size chunks  : {len(fixed_chunks)} chunks")
print(f"Paragraph chunks   : {len(para_chunks)} chunks")
print(f"Section chunks     : {len(section_chunks)} chunks")

print("\n" + "=" * 60)
print("SECTION CHUNKS (best for structured documents):")
for i, chunk in enumerate(section_chunks):
    print(f"\nChunk {i+1} ({len(chunk)} chars):")
    print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    print("-" * 40)

print("\nFor RAG: section chunks preserve document structure.")
print("For legal contracts: split by clause numbers (14.1, 14.2...).")
