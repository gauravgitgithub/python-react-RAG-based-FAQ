from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    file_path: str
    uploaded_by: int


class DocumentUpdate(BaseModel):
    is_active: Optional[bool] = None


class DocumentInDB(DocumentBase):
    id: int
    file_path: str
    is_active: bool
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Document(DocumentInDB):
    pass


class DocumentChunkBase(BaseModel):
    chunk_index: int
    content: str
    start_char: int
    end_char: int


class DocumentChunkCreate(DocumentChunkBase):
    document_id: int
    embedding_id: str


class DocumentChunkInDB(DocumentChunkBase):
    id: int
    document_id: int
    embedding_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentChunk(DocumentChunkInDB):
    pass


class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5


class SourceChunk(BaseModel):
    content: str
    document_name: str
    chunk_index: int
    similarity_score: float


class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    question: str


class DocumentListResponse(BaseModel):
    documents: List[Document]
    total: int
    page: int
    size: int


class DocumentSelectionRequest(BaseModel):
    document_ids: List[int]
    is_active: bool 