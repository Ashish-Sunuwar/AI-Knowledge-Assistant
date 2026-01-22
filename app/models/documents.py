from pydantic import BaseModel
from typing import Dict


class Document(BaseModel):
    doc_id: str
    text: str
    metadata: Dict[str, str] = {}


class Chunk(BaseModel):
    doc_id: str
    chunk_id: str
    text: str
    metadata: Dict[str, str] = {}