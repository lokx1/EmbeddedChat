# Chat API routes with AI provider integration
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json

from ...models.database import get_db
from ...models.user import User
from ...models.conversation import Conversation
from ...models.message import Message
from ...services.chat.ai_chat_service import chat_service
from ...services.ai.provider_service import ai_provider_service
from ...api.middleware.auth import get_current_active_user

router = APIRouter(prefix="/chat", tags=["chat"])

# Request/Response models
class ConversationCreate(BaseModel):
    title: str
    provider_id: Optional[int] = None

class ConversationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    user_id: int
    ai_provider_id: Optional[int]
    model_name: Optional[str]
    system_prompt: Optional[str]
    total_tokens_used: int
    last_message_at: Optional[str]
    created_at: str
    updated_at: str

class MessageCreate(BaseModel):
    content: str
    conversation_id: int

class MessageResponse(BaseModel):
    id: int
    content: str
    message_type: str
    conversation_id: int
    user_id: int
    ai_provider_id: Optional[int]
    model_used: Optional[str]
    tokens_used: Optional[int]
    response_time: Optional[int]
    processing_status: str
    created_at: str

class AIProviderResponse(BaseModel):
    id: int
    name: str
    display_name: str
    provider_type: str
    is_enabled: bool
    is_available: bool
    status_message: Optional[str]
    requires_api_key: bool
    has_api_key: bool
    models: List[Dict[str, Any]]

class ProviderConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_enabled: Optional[bool] = None
    model_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

# AI Providers endpoints
@router.get("/providers", response_model=List[AIProviderResponse])
async def get_ai_providers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all AI providers with their status"""
    try:
        providers = await ai_provider_service.get_all_providers(db)
        return providers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/providers/initialize")
async def initialize_providers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Initialize default AI providers"""
    try:
        await ai_provider_service.initialize_providers(db)
        return {"message": "Providers initialized successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/providers/{provider_id}/check")
async def check_provider_availability(
    provider_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Check availability of a specific AI provider"""
    try:
        result = await ai_provider_service.check_provider_availability(db, provider_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/providers/{provider_id}/config")
async def update_provider_config(
    provider_id: int,
    config: ProviderConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update AI provider configuration"""
    try:
        success = await ai_provider_service.update_provider_config(
            db, provider_id, config.dict(exclude_unset=True)
        )
        if success:
            return {"message": "Provider configuration updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update provider configuration"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Conversation endpoints
@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    try:
        conversation = await chat_service.create_conversation(
            db, current_user.id, conversation_data.title, conversation_data.provider_id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create conversation"
            )
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            description=conversation.description,
            user_id=conversation.user_id,
            ai_provider_id=conversation.ai_provider_id,
            model_name=conversation.model_name,
            system_prompt=conversation.system_prompt,
            total_tokens_used=conversation.total_tokens_used,
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations for the current user"""
    try:
        conversations = await chat_service.get_user_conversations(db, current_user.id)
        return [
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                description=conv.description,
                user_id=conv.user_id,
                ai_provider_id=conv.ai_provider_id,
                model_name=conv.model_name,
                system_prompt=conv.system_prompt,
                total_tokens_used=conv.total_tokens_used,
                last_message_at=conv.last_message_at.isoformat() if conv.last_message_at else None,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat()
            )
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages in a conversation"""
    try:
        messages = await chat_service.get_conversation_messages(db, conversation_id)
        return [
            MessageResponse(
                id=msg.id,
                content=msg.content,
                message_type=msg.message_type.value,
                conversation_id=msg.conversation_id,
                user_id=msg.user_id,
                ai_provider_id=msg.ai_provider_id,
                model_used=msg.model_used,
                tokens_used=msg.tokens_used,
                response_time=msg.response_time,
                processing_status=msg.processing_status,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response"""
    try:
        message = await chat_service.send_message(
            db, message_data.conversation_id, current_user.id, message_data.content
        )
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send message"
            )
        
        return MessageResponse(
            id=message.id,
            content=message.content,
            message_type=message.message_type.value,
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            ai_provider_id=message.ai_provider_id,
            model_used=message.model_used,
            tokens_used=message.tokens_used,
            response_time=message.response_time,
            processing_status=message.processing_status,
            created_at=message.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/stream/{conversation_id}")
async def stream_message(
    conversation_id: int,
    message_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream AI response in real-time"""
    async def generate():
        try:
            async for chunk in chat_service.stream_message(
                db, conversation_id, current_user.id, message_data["content"]
            ):
                yield f"data: {json.dumps(chunk)}\\n\\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# WebSocket endpoint for real-time chat
@router.websocket("/ws/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # For now, echo back - you'd implement proper user auth and message handling
            response = {
                "type": "message",
                "content": f"Echo: {message_data.get('content', '')}",
                "timestamp": "now"
            }
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        print(f"Client disconnected from conversation {conversation_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
