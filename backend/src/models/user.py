# User model
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .database import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    messages = relationship("Message", back_populates="user")
    chat_conversations = relationship("ChatConversation", back_populates="user")
