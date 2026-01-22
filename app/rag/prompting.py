from typing import List
from app.models.ask import SourceItem


SYSTEM_PROMPT = """You are a careful enterprise assistant.
You must only answer using the provided CONTEXT.
If the answer is not in the context, say exactly: "I don't know."
Keep answers short and factual.
"""


def build_prompt(question: str, sources: List[SourceItem]) -> str:
    context_blocks = []
    for s in sources:
        label = s.source_file or s.chunk_id
        context_blocks.append(f"[{label}] {s.preview}")

    context = "\n".join(context_blocks) if context_blocks else "(no context)"

    return f"""{SYSTEM_PROMPT}

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""