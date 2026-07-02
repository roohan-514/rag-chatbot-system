from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str
    k: int = 4


class SourceDocument(BaseModel):
    content: str
    filename: str
    page: Optional[int] = None
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]


class IngestResponse(BaseModel):
    message: str
    filename: str
    chunk_count: int


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
    content_preview: str


class HealthResponse(BaseModel):
    status: str
    collection_size: int
