from typing import List
from app.models.ask import SourceItem

SYSTEM_PROMPT = """You are a careful enterprise assistant.
You MUST only answer using the provided CONTEXT.
If the answer is not explicitly supported by the context, output: I don't know.
You MUST cite which context chunks you used by returning their chunk_id values.
Return your final output ONLY as JSON that matches the required schema.
"""


def build_prompt(question: str, sources: List[SourceItem]) -> str:
    blocks = []
    for s in sources:
        # include chunk_id in the context so the model can cite it
        blocks.append(f"CHUNK_ID: {s.chunk_id}\nTEXT: {s.preview}")

    context = "\n\n".join(blocks) if blocks else "(no context)"

    return f"""{SYSTEM_PROMPT}

CONTEXT:
{context}

QUESTION:
{question}

REQUIRED JSON SCHEMA:
{{
  "answer": "string",
  "used_sources": ["chunk_id", "..."]
}}

RULES:
- If CONTEXT is empty or does not contain the answer: answer must be exactly "I don't know."
- If answer != "I don't know.": used_sources must be non-empty and only contain chunk_ids from CONTEXT.
- Output ONLY valid JSON. No extra keys.

NOW PRODUCE THE JSON:
"""