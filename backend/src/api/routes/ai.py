from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime

from ...services.ai.service_manager import ai_service_manager
from ...services.ai.prompt_manager import prompt_manager
from ...services.ai.response_processor import response_processor

router = APIRouter(prefix="/ai", tags=["AI"])

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    provider: Optional[str] = None
    conversation_id: Optional[str] = None
    stream: bool = True
    temperature: float = 0.7
    max_tokens: int = 2000
    files: List[str] = []
    context: Optional[str] = ""

class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    conversation_id: str
    thinking: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    description: Optional[str] = None
    context_length: Optional[int] = None

@router.on_event("startup")
async def startup_ai_service():
    """Initialize AI service manager on startup"""
    try:
        await ai_service_manager.initialize()
        print("✅ AI Service Manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI Service Manager: {e}")

@router.get("/health")
async def health_check():
    """Check AI service health"""
    try:
        health = await ai_service_manager.health_check()
        return {
            "status": "ok",
            "ai_service": health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/providers")
async def get_providers():
    """Get available AI providers"""
    try:
        providers = await ai_service_manager.get_available_providers()
        return {
            "providers": providers,
            "total": len(providers),
            "default": ai_service_manager.default_provider
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=List[ModelInfo])
async def get_models():
    """Get all available models from all providers"""
    try:
        models = await ai_service_manager.get_all_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{provider}")
async def get_models_by_provider(provider: str):
    """Get models for specific provider"""
    try:
        if provider not in ai_service_manager.providers:
            raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
        
        provider_instance = ai_service_manager.providers[provider]
        if not provider_instance.is_available:
            raise HTTPException(status_code=503, detail=f"Provider {provider} not available")
        
        models = await provider_instance.get_available_models()
        return {
            "provider": provider,
            "models": models,
            "count": len(models)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """Generate AI chat completion"""
    try:
        # Create conversation messages
        messages = prompt_manager.create_conversation_messages(
            user_message=request.message,
            context=request.context or ""
        )
        
        # For non-streaming responses
        if not request.stream:
            full_response = ""
            async for chunk in ai_service_manager.generate_response(
                messages=messages,
                model=request.model,
                provider=request.provider,
                stream=False,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                full_response += chunk
            
            # Process response
            thinking, main_content = response_processor.extract_thinking_content(full_response)
            
            return ChatResponse(
                response=main_content,
                model=request.model or "default",
                provider=request.provider or ai_service_manager.default_provider or "unknown",
                conversation_id=request.conversation_id or f"conv_{datetime.now().timestamp()}",
                thinking=thinking if thinking else None,
                metadata={
                    "word_count": len(main_content.split()),
                    "has_code": bool(response_processor.code_block_pattern.search(main_content)),
                    "processing_time": datetime.now().isoformat()
                }
            )
        
        # For streaming responses
        else:
            async def generate_stream():
                try:
                    async for chunk in ai_service_manager.generate_response(
                        messages=messages,
                        model=request.model,
                        provider=request.provider,
                        stream=True,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens
                    ):
                        # Format as SSE (Server-Sent Events)
                        data = {
                            "content": chunk,
                            "conversation_id": request.conversation_id or f"conv_{datetime.now().timestamp()}",
                            "timestamp": datetime.now().isoformat()
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                    
                    # Send completion signal
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    
                except Exception as e:
                    error_data = {
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/thinking")
async def generate_thinking(request: ChatRequest):
    """Generate thinking steps for a request"""
    try:
        thinking_steps = await ai_service_manager.get_thinking_steps(
            prompt=request.message,
            provider=request.provider,
            context=request.context or ""
        )
        
        return {
            "thinking_steps": thinking_steps,
            "provider": request.provider or ai_service_manager.default_provider,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_response(content: str):
    """Analyze response quality and structure"""
    try:
        analysis = response_processor.analyze_response_quality(content)
        formatted = response_processor.format_markdown(content)
        code_blocks = response_processor.extract_code_blocks(content)
        
        return {
            "quality_metrics": analysis,
            "formatted_content": formatted,
            "code_blocks": code_blocks,
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompts")
async def get_available_prompts():
    """Get available prompt templates"""
    try:
        prompts = prompt_manager.get_available_prompts()
        return {
            "prompts": prompts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prompts/format")
async def format_prompt(template_name: str, variables: Dict[str, Any]):
    """Format a prompt template with variables"""
    try:
        formatted = prompt_manager.format_prompt(template_name, **variables)
        return {
            "template_name": template_name,
            "formatted_prompt": formatted,
            "variables_used": list(variables.keys()),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-memory")
async def extract_memory_from_conversation(
    content: str,
    context: str = "",
    provider: Optional[str] = None
):
    """Extract memory information from conversation"""
    try:
        memory_data = await ai_service_manager.extract_memory(
            content=content,
            context=context,
            provider=provider
        )
        
        return {
            "memory_extracted": memory_data,
            "extraction_method": "ai_powered" if provider else "fallback",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cleanup on shutdown
@router.on_event("shutdown")
async def shutdown_ai_service():
    """Cleanup AI service manager on shutdown"""
    try:
        await ai_service_manager.close()
        print("🔌 AI Service Manager closed")
    except Exception as e:
        print(f"❌ Error closing AI Service Manager: {e}")
