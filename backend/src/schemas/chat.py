# Chat schemas
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from src.models.message import MessageType


class ConversationBase(BaseModel):
    title: str
    description: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Conversation(ConversationBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class MessageBase(BaseModel):
    content: str
    message_type: MessageType


class MessageCreate(MessageBase):
    conversation_id: int


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_edited: Optional[bool] = None


class Message(MessageBase):
    id: int
    conversation_id: int
    user_id: int
    message_metadata: Optional[str] = None
    is_edited: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class ConversationWithMessages(Conversation):
    messages: List[Message] = []


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    message: Message
    conversation: Conversation
