from typing import Dict, List, Any, Optional, AsyncGenerator
import openai
from openai import AsyncOpenAI
import json
import asyncio
from datetime import datetime

from .base_provider import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider for GPT models"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self._name = "openai"
        
    @property
    def name(self) -> str:
        return self._name
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available OpenAI models"""
        try:
            models = await self.client.models.list()
            
            # Filter for chat models
            chat_models = []
            for model in models.data:
                if any(prefix in model.id for prefix in ['gpt-3.5', 'gpt-4', 'gpt-4o']):
                    chat_models.append({
                        "id": model.id,
                        "name": model.id,
                        "description": f"OpenAI {model.id}",
                        "provider": self.name,
                        "type": "chat",
                        "context_length": self._get_context_length(model.id),
                        "created": getattr(model, 'created', None)
                    })
            
            return sorted(chat_models, key=lambda x: x['name'])
            
        except Exception as e:
            print(f"Error fetching OpenAI models: {e}")
            # Return default models if API fails
            return self._get_default_models()
    
    def _get_context_length(self, model_id: str) -> int:
        """Get context length for different models"""
        context_lengths = {
            'gpt-4o': 128000,
            'gpt-4o-mini': 128000,
            'gpt-4-turbo': 128000,
            'gpt-4': 8192,
            'gpt-3.5-turbo': 16385,
        }
        
        for model_prefix, length in context_lengths.items():
            if model_prefix in model_id:
                return length
        
        return 4096  # Default fallback
    
    def _get_default_models(self) -> List[Dict[str, Any]]:
        """Default models when API is unavailable"""
        return [
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "OpenAI GPT-4o - Most capable model",
                "provider": self.name,
                "type": "chat",
                "context_length": 128000
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "description": "OpenAI GPT-4o Mini - Fast and efficient",
                "provider": self.name,
                "type": "chat",
                "context_length": 128000
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "OpenAI GPT-4 Turbo",
                "provider": self.name,
                "type": "chat",
                "context_length": 128000
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "OpenAI GPT-3.5 Turbo",
                "provider": self.name,
                "type": "chat",
                "context_length": 16385
            }
        ]
    
    async def chat(
        self,
        message: str,
        model: str = "gpt-4o",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send chat request to OpenAI"""
        try:
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            if stream:
                return await self._stream_chat(request_params)
            else:
                return await self._regular_chat(request_params)
                
        except Exception as e:
            print(f"Error in OpenAI chat: {e}")
            return {
                "content": f"Error: {str(e)}",
                "error": True,
                "provider": self.name,
                "model": model
            }
    
    async def _regular_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regular (non-streaming) chat"""
        try:
            response = await self.client.chat.completions.create(**params)
            
            choice = response.choices[0]
            content = choice.message.content or ""
            
            return {
                "content": content,
                "role": "assistant",
                "model": params["model"],
                "provider": self.name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "finish_reason": choice.finish_reason,
                "created": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _stream_chat(self, params: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming chat"""
        try:
            response = await self.client.chat.completions.create(**params)
            
            async for chunk in response:
                if chunk.choices:
                    choice = chunk.choices[0]
                    if choice.delta and choice.delta.content:
                        yield {
                            "content": choice.delta.content,
                            "role": "assistant",
                            "model": params["model"],
                            "provider": self.name,
                            "finish_reason": choice.finish_reason,
                            "chunk": True
                        }
                        
        except Exception as e:
            yield {
                "content": f"Stream error: {str(e)}",
                "error": True,
                "provider": self.name,
                "model": params["model"]
            }
    
    async def get_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """Get embeddings for texts"""
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            return [item.embedding for item in response.data]
            
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return []
    
    async def extract_memory(
        self,
        content: str,
        context: str,
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """Extract memory from content"""
        try:
            system_prompt = """
            You are a memory extraction assistant. Extract important, memorable information from the given content.
            Focus on:
            - User preferences and settings
            - Important facts and decisions
            - Personal information shared by the user
            - Technical details that might be referenced later
            - Context that would be useful in future conversations
            
            Return the extracted memory as a JSON object with:
            - extracted_content: The key information to remember
            - relevance_score: A score from 0.0 to 1.0 indicating importance
            - memory_type: The type of memory (preference, fact, decision, etc.)
            """
            
            prompt = f"""
            Context: {context}
            Content to extract memory from: {content}
            
            Extract the most important information that should be remembered for future conversations.
            """
            
            response = await self.chat(
                message=prompt,
                model=model,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=500
            )
            
            # Try to parse JSON response
            try:
                memory_data = json.loads(response.get("content", "{}"))
                return {
                    "extracted_content": memory_data.get("extracted_content", content[:200]),
                    "relevance_score": memory_data.get("relevance_score", 0.5),
                    "memory_type": memory_data.get("memory_type", "general"),
                    "provider": self.name,
                    "model": model
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "extracted_content": response.get("content", content[:200]),
                    "relevance_score": 0.6,
                    "memory_type": "general",
                    "provider": self.name,
                    "model": model
                }
                
        except Exception as e:
            print(f"Error extracting memory: {e}")
            return {
                "extracted_content": content[:200],
                "relevance_score": 0.3,
                "memory_type": "general",
                "error": str(e)
            }
    
    async def get_thinking_steps(
        self,
        message: str,
        context: Optional[str] = None,
        model: str = "gpt-4o"
    ) -> List[str]:
        """Get thinking steps for complex reasoning"""
        try:
            system_prompt = """
            You are an AI assistant that shows your thinking process step by step.
            Break down your reasoning into clear, logical steps before providing an answer.
            Each step should be a single, clear thought or reasoning point.
            """
            
            thinking_prompt = f"""
            Question/Request: {message}
            {f"Context: {context}" if context else ""}
            
            Please show your step-by-step thinking process for addressing this request.
            Format your response as numbered steps, each on a new line starting with a number.
            """
            
            response = await self.chat(
                message=thinking_prompt,
                model=model,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.get("content", "")
            
            # Extract numbered steps
            steps = []
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the step
                    clean_step = line.lstrip('0123456789.-•').strip()
                    if clean_step:
                        steps.append(clean_step)
            
            return steps[:10]  # Limit to 10 steps
            
        except Exception as e:
            print(f"Error getting thinking steps: {e}")
            return [f"Error in thinking process: {str(e)}"]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI API health"""
        try:
            # Simple API call to check connectivity
            models = await self.client.models.list()
            
            return {
                "status": "healthy",
                "provider": self.name,
                "models_available": len(models.data),
                "timestamp": datetime.now().isoformat(),
                "response_time": "< 1s"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "general",
        model: str = "gpt-4o"
    ) -> Dict[str, Any]:
        """Analyze content with specific focus"""
        try:
            analysis_prompts = {
                "sentiment": "Analyze the sentiment of this content. Provide sentiment (positive/negative/neutral) and confidence score.",
                "summary": "Provide a concise summary of this content, highlighting the main points.",
                "keywords": "Extract the most important keywords and topics from this content.",
                "questions": "Generate relevant questions that could be answered by this content.",
                "general": "Provide a general analysis of this content, including key themes, sentiment, and important information."
            }
            
            system_prompt = f"You are an expert content analyst. {analysis_prompts.get(analysis_type, analysis_prompts['general'])}"
            
            response = await self.chat(
                message=f"Please analyze this content:\n\n{content}",
                model=model,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=800
            )
            
            return {
                "analysis": response.get("content", ""),
                "analysis_type": analysis_type,
                "provider": self.name,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "analysis": f"Analysis failed: {str(e)}",
                "error": str(e),
                "analysis_type": analysis_type,
                "provider": self.name
            }
