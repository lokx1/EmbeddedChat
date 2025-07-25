# Document model
from sqlalchemy import Column, String, Integer, ForeignKey, Text, BigInteger, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .database import BaseModel


class DocumentStatus(str, PyEnum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Document(BaseModel):
    __tablename__ = "documents"
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Processing status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADING)
    error_message = Column(Text)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    # Content extracted from document
    extracted_text = Column(Text)
    summary = Column(Text)
    
    # Vector embeddings metadata
    embedding_model = Column(String(100))
    chunk_count = Column(Integer, default=0)
