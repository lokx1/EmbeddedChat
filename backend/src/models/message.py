# Message model
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
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
    
    # Optional metadata
    message_metadata = Column(Text)  # JSON string for additional data
    is_edited = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")
