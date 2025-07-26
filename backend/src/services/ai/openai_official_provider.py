import openai
import asyncio
import json
from typing import Dict, Any, List, AsyncGenerator, Optional
from .base_provider import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    """OpenAI official API provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.organization = config.get('organization')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            if not self.api_key:
                print("OpenAI API key not provided")
                return False
                
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                organization=self.organization,
                base_url=self.base_url
            )
            
            # Test connection by listing models
            models = await self.client.models.list()
            self.is_available = len(models.data) > 0
            return self.is_available
            
        except Exception as e:
            print(f"OpenAI initialization failed: {e}")
            self.is_available = False
            return False
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available OpenAI models"""
        if not self.client:
            return []
            
        try:
            models_response = await self.client.models.list()
            models = []
            
            # Filter for chat completion models
            chat_models = [
                'gpt-4', 'gpt-4-turbo-preview', 'gpt-4-0125-preview',
                'gpt-3.5-turbo', 'gpt-3.5-turbo-16k',
                'gpt-4o', 'gpt-4o-mini'
            ]
            
            for model in models_response.data:
                if any(chat_model in model.id for chat_model in chat_models):
                    models.append({
                        'id': model.id,
                        'name': model.id.replace('-', ' ').title(),
                        'provider': 'openai',
                        'context_length': self._get_context_length(model.id),
                        'created': model.created
                    })
                    
            return sorted(models, key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            print(f"Error fetching OpenAI models: {e}")
            return []
    
    def _get_context_length(self, model_id: str) -> int:
        """Get context length for model"""
        context_lengths = {
            'gpt-4': 8192,
            'gpt-4-turbo': 128000,
            'gpt-4o': 128000,
            'gpt-4o-mini': 128000,
            'gpt-3.5-turbo': 4096,
            'gpt-3.5-turbo-16k': 16384
        }
        
        for model, length in context_lengths.items():
            if model in model_id:
                return length
        return 4096
    
    async def validate_model(self, model: str) -> bool:
        """Validate if model exists"""
        models = await self.get_available_models()
        return any(m['id'] == model for m in models)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate response using OpenAI"""
        
        if not self.client or not self.is_available:
            yield "Error: OpenAI service not available"
            return
            
        formatted_messages = self.format_messages(messages)
        
        try:
            if stream:
                stream_response = await self.client.chat.completions.create(
                    model=model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    **kwargs
                )
                
                async for chunk in stream_response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            else:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                if response.choices:
                    yield response.choices[0].message.content
                    
        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    async def get_thinking_steps(self, prompt: str, context: str = "") -> List[str]:
        """Generate contextual thinking steps for OpenAI"""
        base_steps = await super().get_thinking_steps(prompt, context)
        
        openai_steps = [
            "Connecting to OpenAI API...",
            "Selecting optimal model for the task...",
            "Processing conversation history and context...",
            "Applying advanced reasoning and analysis...",
            "Generating high-quality, contextual response..."
        ]
        
        return openai_steps
    
    async def extract_memory(self, content: str, context: str) -> Dict[str, Any]:
        """Enhanced memory extraction using OpenAI"""
        base_memory = await super().extract_memory(content, context)
        
        # Use OpenAI to extract key concepts if available
        if self.client and len(content) > 50:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "system",
                        "content": "Extract 3-5 key concepts or facts from this conversation that should be remembered for future reference. Return as JSON array."
                    }, {
                        "role": "user", 
                        "content": f"Context: {context}\nContent: {content}"
                    }],
                    max_tokens=200,
                    temperature=0.3
                )
                
                if response.choices:
                    try:
                        key_concepts = json.loads(response.choices[0].message.content)
                        base_memory["key_concepts"] = key_concepts
                        base_memory["relevance_score"] = 0.9
                    except:
                        pass
                        
            except Exception as e:
                print(f"Memory extraction error: {e}")
        
        return base_memory
