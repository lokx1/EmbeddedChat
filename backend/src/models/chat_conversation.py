"""
Chat Conversation Models
Database models for chat conversations and messages
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class ChatConversation(Base):
    """Chat conversation model"""
    __tablename__ = "chat_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New Chat")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # AI Provider settings for this conversation
    ai_provider = Column(String(50), nullable=False, default="openai")
    ai_model = Column(String(100), nullable=False, default="gpt-4o")
    system_prompt = Column(Text, default="You are a helpful AI assistant.")
    temperature = Column(Integer, default=70)  # Stored as int (0.7 * 100)
    max_tokens = Column(Integer, default=2000)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    
    # Statistics
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="chat_conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Response metadata (for assistant messages)
    ai_provider = Column(String(50))
    ai_model = Column(String(100))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    response_time_ms = Column(Integer)
    
    # File attachments (JSON array)
    attachments = Column(JSON)
    
    # Message status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")
