from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator, List
import asyncio
import json

class BaseAIProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace('Provider', '').lower()
        self.is_available = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider and check availability"""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate AI response"""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    async def validate_model(self, model: str) -> bool:
        """Validate if model is available"""
        pass
    
    async def get_thinking_steps(self, prompt: str, context: str = "") -> List[str]:
        """Generate thinking steps for the given prompt"""
        thinking_steps = [
            "Analyzing the user's request...",
            "Retrieving relevant context and information...",
            "Processing available data and constraints...",
            "Formulating comprehensive response strategy...",
            "Generating detailed and accurate response..."
        ]
        return thinking_steps
    
    async def extract_memory(self, content: str, context: str) -> Dict[str, Any]:
        """Extract key information for memory storage"""
        return {
            "type": "conversation",
            "content": content[:500],  # Truncate for storage
            "context": context[:200],
            "relevance_score": 0.8,
            "metadata": {
                "provider": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for provider-specific format"""
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        return formatted
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health status"""
        try:
            models = await self.get_available_models()
            return {
                "status": "healthy" if models else "degraded",
                "available_models": len(models),
                "provider": self.name,
                "config_loaded": bool(self.config)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.name
            }
