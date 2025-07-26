import aiohttp
import asyncio
import json
from typing import Dict, Any, List, AsyncGenerator, Optional
from .base_provider import BaseAIProvider

class OllamaProvider(BaseAIProvider):
    """Ollama local AI provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.timeout = config.get('timeout', 30)
        self.session = None
        
    async def initialize(self) -> bool:
        """Initialize Ollama connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # Test connection
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    self.is_available = True
                    return True
                    
        except Exception as e:
            print(f"Ollama initialization failed: {e}")
            self.is_available = False
            
        return False
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available Ollama models"""
        if not self.session:
            return []
            
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = []
                    for model in data.get('models', []):
                        models.append({
                            'id': model['name'],
                            'name': model['name'],
                            'provider': 'ollama',
                            'size': model.get('size', 0),
                            'modified_at': model.get('modified_at', '')
                        })
                    return models
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            
        return []
    
    async def validate_model(self, model: str) -> bool:
        """Validate if model exists in Ollama"""
        models = await self.get_available_models()
        return any(m['id'] == model for m in models)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate response using Ollama"""
        
        if not self.session or not self.is_available:
            yield "Error: Ollama service not available"
            return
            
        # Format conversation for Ollama
        prompt = self._format_conversation(messages)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                
                if response.status != 200:
                    yield f"Error: Ollama API returned {response.status}"
                    return
                
                if stream:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode().strip())
                                if 'response' in data:
                                    yield data['response']
                                if data.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    data = await response.json()
                    if 'response' in data:
                        yield data['response']
                        
        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into a single prompt for Ollama"""
        formatted_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'user':
                formatted_parts.append(f"Human: {content}")
            elif role == 'assistant':
                formatted_parts.append(f"Assistant: {content}")
            elif role == 'system':
                formatted_parts.append(f"System: {content}")
                
        formatted_parts.append("Assistant:")
        return "\n\n".join(formatted_parts)
    
    async def get_thinking_steps(self, prompt: str, context: str = "") -> List[str]:
        """Generate contextual thinking steps"""
        base_steps = await super().get_thinking_steps(prompt, context)
        
        # Add Ollama-specific thinking
        ollama_steps = [
            "Connecting to local Ollama instance...",
            "Loading and preparing the selected model...",
            "Processing conversation context...",
            "Generating comprehensive response...",
            "Formatting output for optimal readability..."
        ]
        
        return ollama_steps
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
