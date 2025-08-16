"""
Chat API Routes
Handles real-time chat with AI providers
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import asyncio
import json
import time

from ...services.workflow.ai_providers import AIProviderFactory
from ...services.chat_service import ChatService
from ...models.database import get_db
from ...models.user import User
from ...models.document import Document, DocumentStatus
from ...services.document.upload_service import UploadService

router = APIRouter()

# Mock current user function - replace with actual auth
async def get_current_user(request: Request = None) -> User:
    """Get current authenticated user (mock implementation)"""
    # TODO: Implement actual user authentication
    # For now, we'll use a simple header-based mock authentication
    # In a real app, this would validate JWT tokens or session cookies
    
    # Try to get user ID from header or default to 1
    user_id = 1
    username = "test_user"
    email = "test@example.com"
    
    # Mock different users based on some identifier
    # This is just for testing - replace with real auth
    if request:
        # Example: use a header to simulate different users
        mock_user_id = request.headers.get("X-Mock-User-ID")
        if mock_user_id:
            try:
                user_id = int(mock_user_id)
                username = f"user_{user_id}"
                email = f"user{user_id}@example.com"
            except (ValueError, TypeError):
                pass
    
    return User(id=user_id, username=username, email=email)

class ChatMessage(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str

class SendMessageRequest(BaseModel):
    provider: str  # 'openai', 'claude', 'gemini', 'ollama'
    model: str
    apiKey: Optional[str] = None
    temperature: float = 0.7
    maxTokens: int = 2000
    systemPrompt: str = "You are a helpful AI assistant."
    message: str
    conversationId: Optional[int] = None
    conversationHistory: List[ChatMessage] = []
    attachedDocuments: Optional[List[int]] = None  # Document IDs to include in context

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Chat"
    provider: str = "openai"
    model: str = "gpt-4o"
    systemPrompt: str = "You are a helpful AI assistant."
    temperature: float = 0.7
    maxTokens: int = 2000

class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    systemPrompt: Optional[str] = None
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None

class ChatResponse(BaseModel):
    content: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send message to AI provider and get response"""
    try:
        chat_service = ChatService(db)
        # Validate provider
        if request.provider not in ['openai', 'claude', 'gemini', 'ollama']:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
        
        # Validate API key for cloud providers
        if request.provider != 'ollama' and not request.apiKey:
            raise HTTPException(status_code=400, detail=f"API key is required for {request.provider}")
        
        # Create AI provider instance
        if request.provider == 'ollama':
            ai_provider = AIProviderFactory.create_provider(request.provider, base_url="http://localhost:11434")
        else:
            ai_provider = AIProviderFactory.create_provider(request.provider, api_key=request.apiKey)
        
        # Prepare conversation context
        conversation_context = ""
        if request.systemPrompt:
            conversation_context += f"System: {request.systemPrompt}\n\n"
        
        # Add attached documents context if provided
        if request.attachedDocuments:
            upload_service = UploadService()
            document_context = ""
            
            for doc_id in request.attachedDocuments:
                try:
                    # Get document from database
                    result = await db.execute(
                        select(Document).where(
                            and_(
                                Document.id == doc_id,
                                Document.user_id == current_user.id
                            )
                        )
                    )
                    document = result.scalar_one_or_none()
                    
                    if document and document.status == DocumentStatus.READY:
                        # Get document content
                        content = await upload_service.get_document_content(document)
                        if content:
                            document_context += f"\n--- Document: {document.original_filename} ---\n"
                            document_context += content[:2000]  # Limit content to avoid token overflow
                            if len(content) > 2000:
                                document_context += "\n[Document truncated due to length...]"
                            document_context += "\n--- End Document ---\n\n"
                            
                except Exception as e:
                    # Log error but continue with other documents
                    print(f"Error loading document {doc_id}: {e}")
                    continue
            
            if document_context:
                conversation_context += f"Referenced Documents:\n{document_context}\n"
        
        # Add conversation history
        for msg in request.conversationHistory[-10:]:  # Limit to last 10 messages to avoid token limits
            role = "Human" if msg.role == "user" else "Assistant"
            conversation_context += f"{role}: {msg.content}\n"
        
        # Add current message
        conversation_context += f"Human: {request.message}\nAssistant:"
        
        # Generate response
        result = await ai_provider.generate_content(
            prompt=conversation_context,
            output_format="text",
            model_name=request.model,
            temperature=request.temperature,
            max_tokens=request.maxTokens
        )
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown AI generation error')
            raise HTTPException(status_code=500, detail=f"AI generation failed: {error_msg}")
        
        # Save messages to database if conversation ID provided
        start_time = time.time()
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if request.conversationId:
            # Save user message
            await chat_service.add_message(
                conversation_id=request.conversationId,
                role="user",
                content=request.message
            )
            
            # Save AI response
            usage = result.get('metadata', {}).get('usage', {})
            await chat_service.add_message(
                conversation_id=request.conversationId,
                role="assistant",
                content=result['content'],
                ai_provider=request.provider,
                ai_model=request.model,
                prompt_tokens=usage.get('prompt_tokens'),
                completion_tokens=usage.get('completion_tokens'),
                total_tokens=usage.get('total_tokens'),
                response_time_ms=response_time_ms
            )
        
        # Format response
        response = ChatResponse(
            content=result['content'],
            usage=result.get('metadata', {}).get('usage'),
            metadata={
                'provider': request.provider,
                'model': request.model,
                'response_time_ms': response_time_ms,
                'conversation_id': request.conversationId
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/stream")
async def stream_message(request: SendMessageRequest):
    """Stream response from AI provider (for future implementation)"""
    # TODO: Implement streaming response
    raise HTTPException(status_code=501, detail="Streaming not implemented yet")

@router.post("/test-connection")
async def test_connection(provider: str, api_key: Optional[str] = None, model: str = ""):
    """Test connection to AI provider"""
    try:
        # Validate provider
        if provider not in ['openai', 'claude', 'gemini', 'ollama']:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        # Validate API key for cloud providers
        if provider != 'ollama' and not api_key:
            raise HTTPException(status_code=400, detail=f"API key is required for {provider}")
        
        # Create AI provider instance
        if provider == 'ollama':
            ai_provider = AIProviderFactory.create_provider(provider, base_url="http://localhost:11434")
        else:
            ai_provider = AIProviderFactory.create_provider(provider, api_key=api_key)
        
        # Test with simple prompt
        start_time = time.time()
        result = await ai_provider.generate_content(
            prompt="Respond with just 'OK' to test the connection.",
            output_format="text",
            model_name=model,
            temperature=0.1,
            max_tokens=10
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        if result.get('success'):
            return {
                "success": True,
                "message": "Connection successful",
                "response_time_ms": response_time,
                "provider": provider,
                "model": model
            }
        else:
            return {
                "success": False,
                "message": f"Connection failed: {result.get('error', 'Unknown error')}",
                "provider": provider
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}",
            "provider": provider
        }

@router.get("/providers")
async def get_providers():
    """Get list of available AI providers"""
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "Most versatile AI model with excellent reasoning",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                "default_model": "gpt-4o",
                "requires_api_key": True
            },
            {
                "id": "claude",
                "name": "Anthropic Claude",
                "description": "Excellent for analysis and creative writing",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                "default_model": "claude-3-5-sonnet-20241022",
                "requires_api_key": True
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "description": "Fast and efficient with good reasoning capabilities",
                "models": ["gemini-2.5-flash", "gemini-2.5-pro"],
                "default_model": "gemini-2.5-flash",
                "requires_api_key": True
            },
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "description": "Run AI models locally on your machine",
                "models": ["llama3.2", "llama3.2:8b", "mistral", "codellama"],
                "default_model": "llama3.2",
                "requires_api_key": False
            }
        ]
    }

@router.get("/models/{provider}")
async def get_provider_models(provider: str):
    """Get available models for a specific provider"""
    provider_models = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "claude": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        "gemini": ["gemini-2.5-flash", "gemini-2.5-pro"],
        "ollama": ["llama3.2", "llama3.2:8b", "mistral", "codellama"]
    }
    
    if provider not in provider_models:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
    
    return {
        "provider": provider,
        "models": provider_models[provider]
    }

# Conversation Management Endpoints

@router.post("/conversations")
async def create_conversation(
    request: CreateConversationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation"""
    chat_service = ChatService(db)
    
    conversation = await chat_service.create_conversation(
        user_id=current_user.id,
        title=request.title,
        ai_provider=request.provider,
        ai_model=request.model,
        system_prompt=request.systemPrompt,
        temperature=request.temperature,
        max_tokens=request.maxTokens
    )
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "provider": conversation.ai_provider,
        "model": conversation.ai_model,
        "createdAt": conversation.created_at.isoformat(),
        "updatedAt": conversation.updated_at.isoformat(),
        "messageCount": conversation.message_count
    }

@router.get("/conversations")
async def get_conversations(
    limit: int = 50,
    include_archived: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's conversations"""
    chat_service = ChatService(db)
    
    conversations = await chat_service.get_user_conversations(
        user_id=current_user.id,
        limit=limit,
        include_archived=include_archived
    )
    
    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "provider": conv.ai_provider,
                "model": conv.ai_model,
                "createdAt": conv.created_at.isoformat(),
                "updatedAt": conv.updated_at.isoformat(),
                "messageCount": conv.message_count,
                "totalTokens": conv.total_tokens_used,
                "isArchived": conv.is_archived,
                "isFavorite": conv.is_favorite
            }
            for conv in conversations
        ]
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation with messages"""
    chat_service = ChatService(db)
    
    conversation = await chat_service.get_conversation_by_id(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await chat_service.get_conversation_messages(conversation_id, current_user.id)
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "provider": conversation.ai_provider,
        "model": conversation.ai_model,
        "systemPrompt": conversation.system_prompt,
        "temperature": conversation.temperature / 100.0,  # Convert back to float
        "maxTokens": conversation.max_tokens,
        "createdAt": conversation.created_at.isoformat(),
        "updatedAt": conversation.updated_at.isoformat(),
        "messageCount": conversation.message_count,
        "totalTokens": conversation.total_tokens_used,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "createdAt": msg.created_at.isoformat(),
                "aiProvider": msg.ai_provider,
                "aiModel": msg.ai_model,
                "usage": {
                    "promptTokens": msg.prompt_tokens,
                    "completionTokens": msg.completion_tokens,
                    "totalTokens": msg.total_tokens
                } if msg.total_tokens else None,
                "responseTimeMs": msg.response_time_ms,
                "attachments": msg.attachments
            }
            for msg in messages
        ]
    }

@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: int,
    request: UpdateConversationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update conversation settings"""
    chat_service = ChatService(db)
    
    # Filter out None values
    updates = {k: v for k, v in request.dict().items() if v is not None}
    
    conversation = await chat_service.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        **updates
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "provider": conversation.ai_provider,
        "model": conversation.ai_model,
        "updatedAt": conversation.updated_at.isoformat()
    }

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    chat_service = ChatService(db)
    
    success = await chat_service.delete_conversation(conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation deleted successfully"}

@router.post("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a conversation"""
    chat_service = ChatService(db)
    
    success = await chat_service.archive_conversation(conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation archived successfully"}

@router.get("/conversations/search")
async def search_conversations(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search conversations"""
    chat_service = ChatService(db)
    
    conversations = await chat_service.search_conversations(
        user_id=current_user.id,
        search_term=q,
        limit=limit
    )
    
    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "provider": conv.ai_provider,
                "model": conv.ai_model,
                "updatedAt": conv.updated_at.isoformat(),
                "messageCount": conv.message_count
            }
            for conv in conversations
        ]
    }

@router.get("/stats")
async def get_chat_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat statistics for current user"""
    chat_service = ChatService(db)
    
    stats = await chat_service.get_conversation_stats(current_user.id)
    
    return stats