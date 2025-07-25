# Chat routes
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from src.models.database import get_db
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message, MessageType
from src.schemas.chat import (
    ConversationCreate, ConversationUpdate, Conversation as ConversationSchema,
    MessageCreate, Message as MessageSchema,
    ConversationWithMessages, ChatRequest, ChatResponse
)
from src.api.middleware.auth import get_current_active_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    conversation = Conversation(
        title=conversation_data.title,
        description=conversation_data.description,
        user_id=current_user.id
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.get("/conversations", response_model=List[ConversationSchema])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversations"""
    result = await db.execute(
        select(Conversation).where(
            and_(Conversation.user_id == current_user.id, Conversation.is_active == True)
        ).offset(skip).limit(limit)
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation with messages"""
    # Get conversation
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    messages_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    return ConversationWithMessages(
        **conversation.__dict__,
        messages=messages
    )


@router.put("/conversations/{conversation_id}", response_model=ConversationSchema)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a conversation"""
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Update fields
    for field, value in conversation_data.model_dump(exclude_unset=True).items():
        setattr(conversation, field, value)
    
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation (soft delete)"""
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.is_active = False
    await db.commit()


@router.post("/conversations/{conversation_id}/messages", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a message to a conversation"""
    # Verify conversation exists and belongs to user
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
                Conversation.is_active == True
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    message = Message(
        content=message_data.content,
        message_type=message_data.message_type,
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return message


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response (simplified version)"""
    conversation = None
    
    # Get or create conversation
    if chat_request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                and_(
                    Conversation.id == chat_request.conversation_id,
                    Conversation.user_id == current_user.id,
                    Conversation.is_active == True
                )
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
            user_id=current_user.id
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Create user message
    user_message = Message(
        content=chat_request.message,
        message_type=MessageType.USER,
        conversation_id=conversation.id,
        user_id=current_user.id
    )
    
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # TODO: Integrate with AI service for response
    # For now, return a simple echo response
    ai_response_content = f"Echo: {chat_request.message}"
    
    ai_message = Message(
        content=ai_response_content,
        message_type=MessageType.ASSISTANT,
        conversation_id=conversation.id,
        user_id=current_user.id
    )
    
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)
    
    return ChatResponse(
        message=ai_message,
        conversation=conversation
    )
