import asyncio
import json
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from .base_provider import BaseAIProvider
from .ollama_client import OllamaProvider
from .openai_official_provider import OpenAIProvider
from .anthropic_official_provider import AnthropicProvider

class AIServiceManager:
    """Manages multiple AI providers and routes requests"""
    
    def __init__(self, config_path: str = None):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.default_provider = None
        self.config = self._load_config(config_path)
        self.initialized = False
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        config = {
            "ollama": {
                "enabled": True,
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "timeout": 30
            },
            "openai": {
                "enabled": bool(os.getenv("OPENAI_API_KEY")),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "organization": os.getenv("OPENAI_ORGANIZATION"),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            },
            "anthropic": {
                "enabled": bool(os.getenv("ANTHROPIC_API_KEY")),
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
            }
        }
        
        # Load from file if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
                
        return config
    
    async def initialize(self) -> bool:
        """Initialize all enabled providers"""
        print("🚀 Initializing AI Service Manager...")
        
        provider_classes = {
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider
        }
        
        initialization_tasks = []
        
        for provider_name, provider_class in provider_classes.items():
            provider_config = self.config.get(provider_name, {})
            
            if provider_config.get("enabled", False):
                print(f"📡 Initializing {provider_name} provider...")
                provider = provider_class(provider_config)
                self.providers[provider_name] = provider
                
                # Add initialization task
                initialization_tasks.append(self._initialize_provider(provider_name, provider))
        
        # Initialize all providers concurrently
        results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        # Check results and set default provider
        available_providers = []
        for i, result in enumerate(results):
            provider_name = list(provider_classes.keys())[i]
            if isinstance(result, bool) and result:
                available_providers.append(provider_name)
                print(f"✅ {provider_name} provider initialized successfully")
            elif isinstance(result, Exception):
                print(f"❌ {provider_name} provider failed: {result}")
            else:
                print(f"⚠️ {provider_name} provider not available")
        
        # Set default provider (prefer order: anthropic -> openai -> ollama)
        priority_order = ["anthropic", "openai", "ollama"]
        for provider_name in priority_order:
            if provider_name in available_providers:
                self.default_provider = provider_name
                print(f"🎯 Default provider set to: {provider_name}")
                break
        
        self.initialized = len(available_providers) > 0
        
        if self.initialized:
            print(f"🎉 AI Service Manager initialized with {len(available_providers)} providers")
        else:
            print("⚠️ No AI providers available")
            
        return self.initialized
    
    async def _initialize_provider(self, name: str, provider: BaseAIProvider) -> bool:
        """Initialize a single provider"""
        try:
            return await provider.initialize()
        except Exception as e:
            print(f"Provider {name} initialization error: {e}")
            return False
    
    async def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their status"""
        providers_info = []
        
        for name, provider in self.providers.items():
            if provider.is_available:
                health = await provider.health_check()
                models = await provider.get_available_models()
                
                providers_info.append({
                    "name": name,
                    "status": health.get("status", "unknown"),
                    "models_count": len(models),
                    "is_default": name == self.default_provider,
                    "models": models[:5]  # First 5 models for preview
                })
                
        return providers_info
    
    async def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all available models from all providers"""
        all_models = []
        
        for provider_name, provider in self.providers.items():
            if provider.is_available:
                try:
                    models = await provider.get_available_models()
                    for model in models:
                        model["provider_name"] = provider_name
                        all_models.append(model)
                except Exception as e:
                    print(f"Error getting models from {provider_name}: {e}")
        
        return sorted(all_models, key=lambda x: (x.get("provider_name", ""), x.get("name", "")))
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        provider: str = None,
        stream: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate AI response using specified or default provider"""
        
        if not self.initialized:
            yield "Error: AI Service Manager not initialized"
            return
        
        # Determine provider and model
        target_provider = provider or self.default_provider
        if not target_provider or target_provider not in self.providers:
            yield "Error: No suitable AI provider available"
            return
            
        provider_instance = self.providers[target_provider]
        if not provider_instance.is_available:
            yield f"Error: {target_provider} provider not available"
            return
        
        # Use default model if not specified
        if not model:
            models = await provider_instance.get_available_models()
            if models:
                model = models[0]["id"]
            else:
                yield "Error: No models available"
                return
        
        # Validate model
        if not await provider_instance.validate_model(model):
            yield f"Error: Model {model} not available in {target_provider}"
            return
        
        # Generate response
        try:
            async for chunk in provider_instance.generate_response(
                messages=messages,
                model=model,
                stream=stream,
                **kwargs
            ):
                yield chunk
                
        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    async def get_thinking_steps(self, prompt: str, provider: str = None, context: str = "") -> List[str]:
        """Get thinking steps from specified provider"""
        target_provider = provider or self.default_provider
        
        if target_provider and target_provider in self.providers:
            provider_instance = self.providers[target_provider]
            if provider_instance.is_available:
                return await provider_instance.get_thinking_steps(prompt, context)
        
        # Fallback thinking steps
        return [
            "Processing your request...",
            "Analyzing available information...", 
            "Formulating comprehensive response...",
            "Ensuring accuracy and relevance..."
        ]
    
    async def extract_memory(self, content: str, context: str, provider: str = None) -> Dict[str, Any]:
        """Extract memory using AI provider"""
        target_provider = provider or self.default_provider
        
        if target_provider and target_provider in self.providers:
            provider_instance = self.providers[target_provider]
            if provider_instance.is_available:
                return await provider_instance.extract_memory(content, context)
        
        # Fallback memory extraction
        return {
            "type": "conversation",
            "content": content[:500],
            "context": context[:200],
            "relevance_score": 0.7,
            "provider": "fallback"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        health_status = {
            "overall_status": "healthy" if self.initialized else "unhealthy",
            "providers": {},
            "default_provider": self.default_provider,
            "total_models": 0
        }
        
        for name, provider in self.providers.items():
            if provider.is_available:
                provider_health = await provider.health_check()
                health_status["providers"][name] = provider_health
                health_status["total_models"] += provider_health.get("available_models", 0)
        
        return health_status
    
    async def close(self):
        """Close all provider connections"""
        for provider in self.providers.values():
            if hasattr(provider, 'close') and callable(provider.close):
                try:
                    await provider.close()
                except Exception as e:
                    print(f"Error closing provider: {e}")
        
        self.providers.clear()
        self.initialized = False
        print("🔌 AI Service Manager closed")

# Global instance
ai_service_manager = AIServiceManager()