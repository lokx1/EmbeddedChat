#!/usr/bin/env python3
"""
Script to populate default AI providers in the database
Run this after running migrations to set up initial providers
"""

import asyncio
import sys
import os

# Add the backend src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.database import Base
from src.models.ai_provider import AIProvider, AIModel
from src.core.config import settings

async def create_default_providers():
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Ollama Provider
            ollama_provider = AIProvider(
                name="ollama",
                display_name="Ollama (Local)",
                provider_type="ollama",
                is_enabled=True,
                base_url="http://localhost:11434",
                config={
                    "default_model": "llama2",
                    "timeout": 60,
                    "max_retries": 3
                }
            )
            session.add(ollama_provider)
            await session.flush()  # To get the ID
            
            # Ollama models
            ollama_models = [
                AIModel(
                    provider_id=ollama_provider.id,
                    model_id="llama2",
                    model_name="Llama 2",
                    description="Meta's Llama 2 model",
                    supports_streaming=True,
                    supports_functions=False,
                    supports_vision=False,
                    context_length=4096
                ),
                AIModel(
                    provider_id=ollama_provider.id,
                    model_id="codellama",
                    model_name="Code Llama",
                    description="Code generation model",
                    supports_streaming=True,
                    supports_functions=False,
                    supports_vision=False,
                    context_length=4096
                ),
                AIModel(
                    provider_id=ollama_provider.id,
                    model_id="mistral",
                    model_name="Mistral",
                    description="Mistral 7B model",
                    supports_streaming=True,
                    supports_functions=False,
                    supports_vision=False,
                    context_length=8192
                )
            ]
            
            # OpenAI Provider
            openai_provider = AIProvider(
                name="openai",
                display_name="OpenAI",
                provider_type="openai",
                is_enabled=False,  # Disabled by default until API key is set
                base_url="https://api.openai.com/v1",
                config={
                    "timeout": 60,
                    "max_retries": 3,
                    "organization": None
                }
            )
            session.add(openai_provider)
            await session.flush()
            
            # OpenAI models
            openai_models = [
                AIModel(
                    provider_id=openai_provider.id,
                    model_id="gpt-4",
                    model_name="GPT-4",
                    description="OpenAI's most capable model",
                    supports_streaming=True,
                    supports_functions=True,
                    supports_vision=False,
                    max_tokens=8192,
                    context_length=8192,
                    input_cost_per_token="0.00003",
                    output_cost_per_token="0.00006"
                ),
                AIModel(
                    provider_id=openai_provider.id,
                    model_id="gpt-4-1106-preview",
                    model_name="GPT-4 Turbo",
                    description="GPT-4 with 128K context",
                    supports_streaming=True,
                    supports_functions=True,
                    supports_vision=False,
                    max_tokens=4096,
                    context_length=128000,
                    input_cost_per_token="0.00001",
                    output_cost_per_token="0.00003"
                ),
                AIModel(
                    provider_id=openai_provider.id,
                    model_id="gpt-3.5-turbo",
                    model_name="GPT-3.5 Turbo",
                    description="Fast and efficient model",
                    supports_streaming=True,
                    supports_functions=True,
                    supports_vision=False,
                    max_tokens=4096,
                    context_length=16385,
                    input_cost_per_token="0.0000015",
                    output_cost_per_token="0.000002"
                )
            ]
            
            # Claude Provider
            claude_provider = AIProvider(
                name="claude",
                display_name="Anthropic Claude",
                provider_type="anthropic",
                is_enabled=False,  # Disabled by default until API key is set
                base_url="https://api.anthropic.com/v1",
                config={
                    "timeout": 60,
                    "max_retries": 3,
                    "anthropic_version": "2023-06-01"
                }
            )
            session.add(claude_provider)
            await session.flush()
            
            # Claude models
            claude_models = [
                AIModel(
                    provider_id=claude_provider.id,
                    model_id="claude-3-opus-20240229",
                    model_name="Claude 3 Opus",
                    description="Anthropic's most powerful model",
                    supports_streaming=True,
                    supports_functions=False,
                    supports_vision=True,
                    max_tokens=4096,
                    context_length=200000,
                    input_cost_per_token="0.000015",
                    output_cost_per_token="0.000075"
                ),
                AIModel(
                    provider_id=claude_provider.id,
                    model_id="claude-3-sonnet-20240229",
                    model_name="Claude 3 Sonnet",
                    description="Balanced intelligence and speed",
                    supports_streaming=True,
                    supports_functions=False,
                    supports_vision=True,
                    max_tokens=4096,
                    context_length=200000,
                    input_cost_per_token="0.000003",
                    output_cost_per_token="0.000015"
                ),
                AIModel(
                    provider_id=claude_provider.id,
                    model_id="claude-3-haiku-20240307",
                    model_name="Claude 3 Haiku",
                    description="Fast and cost-effective",
                    supports_streaming=True,
                    supports_functions=False,
                    supports_vision=True,
                    max_tokens=4096,
                    context_length=200000,
                    input_cost_per_token="0.00000025",
                    output_cost_per_token="0.00000125"
                )
            ]
            
            # Add all models
            for model in ollama_models + openai_models + claude_models:
                session.add(model)
            
            await session.commit()
            print("✅ Default AI providers and models created successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating default providers: {e}")
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_default_providers())
