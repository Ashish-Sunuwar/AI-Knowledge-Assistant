from pydantic import BaseModel, Field
from typing import List


class GroundedAnswer(BaseModel):
    """
    The ONLY valid final output we accept from the LLM.
    """
    answer: str = Field(..., description="Final answer. If not supported by context, must be exactly: I don't know.")
    used_sources: List[str] = Field(default_factory=list, description="List of chunk_id values used to answer.")