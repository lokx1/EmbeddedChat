# AI Provider Management Service
import asyncio
import httpx
import openai
import anthropic
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging

from ...models.ai_provider import AIProvider, AIModel
from ...utils.logger import get_logger

logger = get_logger(__name__)

class AIProviderService:
    """Service for managing AI providers and their availability"""
    
    def __init__(self):
        self.providers_config = {
            "ollama": {
                "display_name": "Ollama (Local)",
                "provider_type": "local",
                "default_base_url": "http://localhost:11434",
                "check_endpoint": "/api/tags",
                "requires_api_key": False
            },
            "openai": {
                "display_name": "OpenAI GPT",
                "provider_type": "api",
                "default_base_url": "https://api.openai.com/v1",
                "check_endpoint": "/models",
                "requires_api_key": True
            },
            "claude": {
                "display_name": "Anthropic Claude",
                "provider_type": "api",
                "default_base_url": "https://api.anthropic.com/v1",
                "check_endpoint": "/messages",
                "requires_api_key": True
            }
        }
    
    async def initialize_providers(self, db: AsyncSession):
        """Initialize default providers if they don't exist"""
        try:
            for provider_name, config in self.providers_config.items():
                # Check if provider exists
                result = await db.execute(
                    select(AIProvider).where(AIProvider.name == provider_name)
                )
                existing_provider = result.scalar_one_or_none()
                
                if not existing_provider:
                    # Create new provider
                    provider = AIProvider(
                        name=provider_name,
                        display_name=config["display_name"],
                        provider_type=config["provider_type"],
                        base_url=config["default_base_url"],
                        is_enabled=False,
                        is_available=False
                    )
                    db.add(provider)
                    logger.info(f"Created AI provider: {provider_name}")
            
            await db.commit()
            logger.info("Initialized AI providers")
            
        except Exception as e:
            logger.error(f"Error initializing providers: {e}")
            await db.rollback()
            raise
    
    async def check_ollama_availability(self, base_url: str) -> Dict[str, Any]:
        """Check if Ollama is available and get models"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{base_url}/api/tags")
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    
                    for model in data.get("models", []):
                        models.append({
                            "model_id": model["name"],
                            "model_name": model["name"],
                            "description": f"Ollama model: {model['name']}",
                            "supports_streaming": True,
                            "supports_functions": False,
                            "context_length": model.get("details", {}).get("parameter_size", "Unknown")
                        })
                    
                    return {
                        "available": True,
                        "models": models,
                        "status": "Connected successfully"
                    }
                else:
                    return {
                        "available": False,
                        "models": [],
                        "status": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "available": False,
                "models": [],
                "status": f"Connection error: {str(e)}"
            }
    
    async def check_openai_availability(self, api_key: str) -> Dict[str, Any]:
        """Check OpenAI API key and get models"""
        try:
            client = openai.AsyncOpenAI(api_key=api_key)
            models_response = await client.models.list()
            
            # Filter to common chat models
            chat_models = []
            common_models = ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
            
            for model in models_response.data:
                if any(common in model.id for common in common_models):
                    chat_models.append({
                        "model_id": model.id,
                        "model_name": model.id.replace("-", " ").title(),
                        "description": f"OpenAI model: {model.id}",
                        "supports_streaming": True,
                        "supports_functions": True,
                        "supports_vision": "vision" in model.id or "4o" in model.id,
                        "context_length": self._get_openai_context_length(model.id)
                    })
            
            return {
                "available": True,
                "models": chat_models,
                "status": "API key valid"
            }
            
        except Exception as e:
            return {
                "available": False,
                "models": [],
                "status": f"API error: {str(e)}"
            }
    
    async def check_claude_availability(self, api_key: str) -> Dict[str, Any]:
        """Check Claude API key availability"""
        try:
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            # Try a minimal request to check API key
            await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            
            # Define Claude models
            claude_models = [
                {
                    "model_id": "claude-3-opus-20240229",
                    "model_name": "Claude 3 Opus",
                    "description": "Most powerful Claude model",
                    "supports_streaming": True,
                    "supports_functions": True,
                    "supports_vision": True,
                    "context_length": 200000
                },
                {
                    "model_id": "claude-3-sonnet-20240229",
                    "model_name": "Claude 3 Sonnet",
                    "description": "Balanced Claude model",
                    "supports_streaming": True,
                    "supports_functions": True,
                    "supports_vision": True,
                    "context_length": 200000
                },
                {
                    "model_id": "claude-3-haiku-20240307",
                    "model_name": "Claude 3 Haiku",
                    "description": "Fastest Claude model",
                    "supports_streaming": True,
                    "supports_functions": True,
                    "supports_vision": True,
                    "context_length": 200000
                }
            ]
            
            return {
                "available": True,
                "models": claude_models,
                "status": "API key valid"
            }
            
        except Exception as e:
            return {
                "available": False,
                "models": [],
                "status": f"API error: {str(e)}"
            }
    
    def _get_openai_context_length(self, model_id: str) -> int:
        """Get context length for OpenAI models"""
        context_lengths = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "gpt-4o": 128000,
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-16k": 16385
        }
        
        for model, length in context_lengths.items():
            if model in model_id:
                return length
        return 8192  # Default
    
    async def check_provider_availability(self, db: AsyncSession, provider_id: int) -> Dict[str, Any]:
        """Check availability of a specific provider"""
        try:
            result = await db.execute(
                select(AIProvider).where(AIProvider.id == provider_id)
            )
            provider = result.scalar_one_or_none()
            
            if not provider:
                return {"error": "Provider not found"}
            
            if provider.name == "ollama":
                check_result = await self.check_ollama_availability(provider.base_url)
            elif provider.name == "openai":
                if not provider.api_key:
                    return {"available": False, "status": "API key required"}
                check_result = await self.check_openai_availability(provider.api_key)
            elif provider.name == "claude":
                if not provider.api_key:
                    return {"available": False, "status": "API key required"}
                check_result = await self.check_claude_availability(provider.api_key)
            else:
                return {"available": False, "status": "Unknown provider"}
            
            # Update provider status
            await db.execute(
                update(AIProvider)
                .where(AIProvider.id == provider_id)
                .values(
                    is_available=check_result["available"],
                    status_message=check_result["status"]
                )
            )
            
            # Update models if available
            if check_result["available"] and check_result["models"]:
                await self._update_provider_models(db, provider_id, check_result["models"])
            
            await db.commit()
            
            return check_result
            
        except Exception as e:
            logger.error(f"Error checking provider availability: {e}")
            await db.rollback()
            return {"available": False, "status": f"Error: {str(e)}"}
    
    async def _update_provider_models(self, db: AsyncSession, provider_id: int, models: List[Dict]):
        """Update available models for a provider"""
        try:
            # Delete existing models
            await db.execute(
                select(AIModel).where(AIModel.provider_id == provider_id)
            )
            
            # Add new models
            for model_data in models:
                model = AIModel(
                    provider_id=provider_id,
                    model_id=model_data["model_id"],
                    model_name=model_data["model_name"],
                    description=model_data.get("description"),
                    supports_streaming=model_data.get("supports_streaming", True),
                    supports_functions=model_data.get("supports_functions", False),
                    supports_vision=model_data.get("supports_vision", False),
                    context_length=model_data.get("context_length")
                )
                db.add(model)
                
        except Exception as e:
            logger.error(f"Error updating provider models: {e}")
    
    async def get_all_providers(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get all providers with their status"""
        try:
            result = await db.execute(select(AIProvider))
            providers = result.scalars().all()
            
            provider_list = []
            for provider in providers:
                # Get models for this provider
                models_result = await db.execute(
                    select(AIModel).where(AIModel.provider_id == provider.id)
                )
                models = models_result.scalars().all()
                
                provider_list.append({
                    "id": provider.id,
                    "name": provider.name,
                    "display_name": provider.display_name,
                    "provider_type": provider.provider_type,
                    "is_enabled": provider.is_enabled,
                    "is_available": provider.is_available,
                    "status_message": provider.status_message,
                    "requires_api_key": self.providers_config[provider.name]["requires_api_key"],
                    "has_api_key": bool(provider.api_key),
                    "base_url": provider.base_url,
                    "models": [
                        {
                            "id": model.id,
                            "model_id": model.model_id,
                            "model_name": model.model_name,
                            "description": model.description,
                            "supports_streaming": model.supports_streaming,
                            "supports_functions": model.supports_functions,
                            "supports_vision": model.supports_vision,
                            "context_length": model.context_length
                        }
                        for model in models
                    ]
                })
            
            return provider_list
            
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            return []
    
    async def update_provider_config(self, db: AsyncSession, provider_id: int, config: Dict[str, Any]) -> bool:
        """Update provider configuration"""
        try:
            update_data = {}
            
            if "api_key" in config:
                update_data["api_key"] = config["api_key"]
            if "base_url" in config:
                update_data["base_url"] = config["base_url"]
            if "is_enabled" in config:
                update_data["is_enabled"] = config["is_enabled"]
            if "model_name" in config:
                update_data["model_name"] = config["model_name"]
            if "config" in config:
                update_data["config"] = config["config"]
            
            await db.execute(
                update(AIProvider)
                .where(AIProvider.id == provider_id)
                .values(**update_data)
            )
            
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating provider config: {e}")
            await db.rollback()
            return False

# Global instance
ai_provider_service = AIProviderService()
