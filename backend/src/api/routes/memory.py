from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ...models.database import get_db
from ...models.conversation import Conversation
from ...models.message import Message
from ...services.ai.service_manager import ai_service_manager

router = APIRouter(prefix="/memory", tags=["Memory"])

class Memory(BaseModel):
    id: str
    content: str
    context: str
    relevance_score: Optional[float] = None
    created_at: datetime
    conversation_id: Optional[str] = None

class ConversationSummary(BaseModel):
    id: str
    summary: str
    key_points: List[str]
    created_at: datetime
    conversation_id: str

class MemoryCreateRequest(BaseModel):
    content: str
    context: str
    conversation_id: Optional[str] = None

class MemoryUpdateRequest(BaseModel):
    content: Optional[str] = None
    context: Optional[str] = None
    relevance_score: Optional[float] = None

class MemoryExtractRequest(BaseModel):
    content: str
    context: str
    conversation_id: Optional[str] = None

# In-memory storage for demo (replace with proper database)
memories_store: Dict[str, Memory] = {}
summaries_store: Dict[str, ConversationSummary] = {}

@router.get("/", response_model=List[Memory])
async def get_memories(
    limit: int = 50,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all memories or filter by conversation"""
    try:
        # Filter memories
        filtered_memories = []
        for memory in memories_store.values():
            if conversation_id and memory.conversation_id != conversation_id:
                continue
            filtered_memories.append(memory)
        
        # Sort by relevance score and creation date
        filtered_memories.sort(
            key=lambda x: (x.relevance_score or 0, x.created_at),
            reverse=True
        )
        
        return filtered_memories[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching memories: {str(e)}")


@router.get("/summaries", response_model=List[ConversationSummary])
async def get_conversation_summaries(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get conversation summaries"""
    try:
        summaries = list(summaries_store.values())
        summaries.sort(key=lambda x: x.created_at, reverse=True)
        return summaries[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summaries: {str(e)}")


@router.post("/", response_model=Memory)
async def create_memory(
    request: MemoryCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new memory"""
    try:
        memory_id = f"mem_{len(memories_store) + 1}_{int(datetime.now().timestamp())}"
        
        memory = Memory(
            id=memory_id,
            content=request.content,
            context=request.context,
            created_at=datetime.now(),
            conversation_id=request.conversation_id
        )
        
        memories_store[memory_id] = memory
        return memory
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating memory: {str(e)}")


@router.put("/{memory_id}", response_model=Memory)
async def update_memory(
    memory_id: str,
    request: MemoryUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update an existing memory"""
    try:
        if memory_id not in memories_store:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        memory = memories_store[memory_id]
        
        if request.content is not None:
            memory.content = request.content
        if request.context is not None:
            memory.context = request.context
        if request.relevance_score is not None:
            memory.relevance_score = request.relevance_score
        
        memories_store[memory_id] = memory
        return memory
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating memory: {str(e)}")


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    db: Session = Depends(get_db)
):
    """Delete a memory"""
    try:
        if memory_id not in memories_store:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        del memories_store[memory_id]
        return {"status": "deleted", "memory_id": memory_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting memory: {str(e)}")


@router.post("/extract", response_model=Memory)
async def extract_memory(
    request: MemoryExtractRequest,
    db: Session = Depends(get_db)
):
    """Extract memory from content using AI"""
    try:
        # Use AI service to extract memory
        available_providers = await ai_service_manager.get_available_providers()
        if not available_providers:
            raise HTTPException(status_code=503, detail="No AI providers available")
        
        # Use the first available provider
        provider_name = available_providers[0]
        provider = ai_service_manager.get_provider(provider_name)
        
        # Extract memory using AI
        memory_response = await provider.extract_memory(
            content=request.content,
            context=request.context
        )
        
        # Create memory from AI response
        memory_id = f"mem_{len(memories_store) + 1}_{int(datetime.now().timestamp())}"
        
        memory = Memory(
            id=memory_id,
            content=memory_response.get("extracted_content", request.content),
            context=request.context,
            relevance_score=memory_response.get("relevance_score", 0.8),
            created_at=datetime.now(),
            conversation_id=request.conversation_id
        )
        
        memories_store[memory_id] = memory
        return memory
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting memory: {str(e)}")


@router.post("/summarize/{conversation_id}", response_model=ConversationSummary)
async def summarize_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Create a summary of a conversation"""
    try:
        # Get conversation and messages
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages found in conversation")
        
        # Use AI to summarize
        available_providers = await ai_service_manager.get_available_providers()
        if not available_providers:
            raise HTTPException(status_code=503, detail="No AI providers available")
        
        provider_name = available_providers[0]
        provider = ai_service_manager.get_provider(provider_name)
        
        # Prepare conversation text
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in messages
        ])
        
        # Get summary from AI
        summary_response = await provider.chat(
            message=f"Please summarize this conversation and extract key points:\n\n{conversation_text}",
            system_prompt="You are a helpful assistant that creates concise summaries and extracts key points from conversations.",
            temperature=0.3
        )
        
        # Parse AI response (simplified)
        summary_text = summary_response.get("content", "Summary not available")
        key_points = [
            point.strip() 
            for point in summary_text.split("\n") 
            if point.strip().startswith("-") or point.strip().startswith("•")
        ]
        
        # Create summary
        summary_id = f"sum_{conversation_id}_{int(datetime.now().timestamp())}"
        
        summary = ConversationSummary(
            id=summary_id,
            summary=summary_text,
            key_points=key_points,
            created_at=datetime.now(),
            conversation_id=conversation_id
        )
        
        summaries_store[summary_id] = summary
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing conversation: {str(e)}")


@router.get("/search")
async def search_memories(
    query: str,
    limit: int = 10,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search memories by content or context"""
    try:
        if not query.strip():
            return {"memories": [], "count": 0}
        
        query_lower = query.lower()
        matched_memories = []
        
        for memory in memories_store.values():
            if conversation_id and memory.conversation_id != conversation_id:
                continue
                
            # Simple text search
            if (query_lower in memory.content.lower() or 
                query_lower in memory.context.lower()):
                matched_memories.append(memory)
        
        # Sort by relevance score
        matched_memories.sort(
            key=lambda x: x.relevance_score or 0,
            reverse=True
        )
        
        return {
            "memories": matched_memories[:limit],
            "count": len(matched_memories),
            "query": query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memories: {str(e)}")


@router.get("/stats")
async def get_memory_stats(db: Session = Depends(get_db)):
    """Get memory statistics"""
    try:
        total_memories = len(memories_store)
        total_summaries = len(summaries_store)
        
        # Count by conversation
        conversation_counts = {}
        for memory in memories_store.values():
            if memory.conversation_id:
                conversation_counts[memory.conversation_id] = conversation_counts.get(
                    memory.conversation_id, 0
                ) + 1
        
        # Average relevance score
        relevance_scores = [
            memory.relevance_score 
            for memory in memories_store.values() 
            if memory.relevance_score is not None
        ]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        return {
            "total_memories": total_memories,
            "total_summaries": total_summaries,
            "conversations_with_memories": len(conversation_counts),
            "avg_memories_per_conversation": (
                sum(conversation_counts.values()) / len(conversation_counts) 
                if conversation_counts else 0
            ),
            "avg_relevance_score": round(avg_relevance, 2),
            "memory_distribution": conversation_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting memory stats: {str(e)}")


# Initialize some sample memories for demo
def init_sample_memories():
    """Initialize sample memories for demonstration"""
    sample_memories = [
        {
            "content": "User prefers dark mode for all applications",
            "context": "UI preferences discussion",
            "relevance_score": 0.9
        },
        {
            "content": "User is working on a React TypeScript project with FastAPI backend",
            "context": "Technical stack discussion",
            "relevance_score": 0.95
        },
        {
            "content": "User mentioned they are located in Vietnam timezone",
            "context": "Timezone and scheduling preferences",
            "relevance_score": 0.7
        }
    ]
    
    for i, mem_data in enumerate(sample_memories):
        memory_id = f"sample_mem_{i + 1}"
        memory = Memory(
            id=memory_id,
            content=mem_data["content"],
            context=mem_data["context"],
            relevance_score=mem_data["relevance_score"],
            created_at=datetime.now(),
            conversation_id=None
        )
        memories_store[memory_id] = memory

# Initialize sample data
init_sample_memories()
