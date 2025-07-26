# Message model
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import BaseModel


class MessageType(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    __tablename__ = "messages"
    
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # AI Response metadata
    ai_provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    model_used = Column(String(200), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Integer, nullable=True)  # milliseconds
    
    # Message metadata
    message_metadata = Column(JSON, nullable=True)  # Additional data, attachments, etc.
    is_edited = Column(Boolean, default=False)
    
    # Message processing
    processing_status = Column(String(50), default="completed")  # pending, processing, completed, error
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")
    ai_provider = relationship("AIProvider")
