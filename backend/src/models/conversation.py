# Conversation model
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # AI Provider settings for this conversation
    ai_provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    model_name = Column(String(200), nullable=True)
    
    # Conversation settings
    system_prompt = Column(Text, nullable=True)
    conversation_settings = Column(JSON, nullable=True)  # temperature, max_tokens, etc.
    
    # Memory and context
    memory_summary = Column(Text, nullable=True)  # Summarized conversation context
    total_tokens_used = Column(Integer, default=0)
    
    # Timestamps
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    ai_provider = relationship("AIProvider")
