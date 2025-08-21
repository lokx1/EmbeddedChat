# Document schemas
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from src.models.document import DocumentStatus


class DocumentBase(BaseModel):
    filename: str
    original_filename: str


class DocumentCreate(DocumentBase):
    file_size: int
    mime_type: str
    
    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        max_size = 200 * 1024 * 1024  # 200MB to match route
        if v > max_size:
            raise ValueError(f'File size cannot exceed {max_size} bytes')
        return v


class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = None
    extracted_text: Optional[str] = None
    summary: Optional[str] = None


class Document(DocumentBase):
    id: int
    file_path: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    error_message: Optional[str] = None
    user_id: int
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    embedding_model: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class DocumentList(BaseModel):
    documents: List[Document]
    total: int
    page: int
    size: int
