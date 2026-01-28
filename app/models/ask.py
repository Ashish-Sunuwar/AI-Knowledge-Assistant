from pydantic import BaseModel, Field
from typing import Optional, List


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)


class SourceItem(BaseModel):
    chunk_id: str
    source_file: Optional[str] = None
    score: float
    preview: str

class AnswerData(BaseModel):
    answer: str
    sources: List[SourceItem] = []
    used_sources: List[str] = []
    confidence: Optional[float] = None