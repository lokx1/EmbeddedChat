# AI Provider models for configuration and management
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .database import Base

class ProviderType(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"

class AIProvider(Base):
    """AI Provider configuration model"""
    __tablename__ = "ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # ollama, openai, claude
    display_name = Column(String(200), nullable=False)
    provider_type = Column(String(50), nullable=False)  # local, api
    is_enabled = Column(Boolean, default=False)
    is_available = Column(Boolean, default=False)
    
    # Configuration fields
    api_key = Column(Text, nullable=True)  # For OpenAI, Claude
    base_url = Column(String(500), nullable=True)  # For Ollama or custom endpoints
    model_name = Column(String(200), nullable=True)  # Default model
    
    # Provider specific settings
    config = Column(JSON, nullable=True)  # Additional settings like temperature, max_tokens
    
    # Status tracking
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    status_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="ai_provider")
    messages = relationship("Message", back_populates="ai_provider")
    models = relationship("AIModel", back_populates="provider")
    
    @property
    def requires_api_key(self) -> bool:
        """Check if this provider requires an API key"""
        return self.provider_type in [ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.HUGGINGFACE]
    
    @property
    def has_api_key(self) -> bool:
        """Check if this provider has an API key configured"""
        return bool(self.api_key)
    
    def get_config(self) -> dict:
        """Get provider configuration"""
        return self.config if self.config else {}
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "provider_type": self.provider_type,
            "is_enabled": self.is_enabled,
            "is_available": self.is_available,
            "status_message": self.status_message,
            "requires_api_key": self.requires_api_key,
            "has_api_key": self.has_api_key,
            "base_url": self.base_url,
            "model_name": self.model_name,
            "models": [model.to_dict() for model in self.models] if self.models else [],
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class AIModel(Base):
    """Available AI models for each provider"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    model_id = Column(String(200), nullable=False)  # Model identifier (e.g., gpt-4, claude-3)
    model_name = Column(String(200), nullable=False)  # Display name
    description = Column(Text, nullable=True)
    
    # Model capabilities
    supports_streaming = Column(Boolean, default=True)
    supports_functions = Column(Boolean, default=False)
    supports_vision = Column(Boolean, default=False)
    
    # Limits
    max_tokens = Column(Integer, nullable=True)
    context_length = Column(Integer, nullable=True)
    
    # Pricing (tokens per USD)
    input_cost_per_token = Column(String(20), nullable=True)
    output_cost_per_token = Column(String(20), nullable=True)
    
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    provider = relationship("AIProvider", back_populates="models")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "description": self.description,
            "supports_streaming": self.supports_streaming,
            "supports_functions": self.supports_functions,
            "supports_vision": self.supports_vision,
            "max_tokens": self.max_tokens,
            "context_length": self.context_length,
            "input_cost_per_token": self.input_cost_per_token,
            "output_cost_per_token": self.output_cost_per_token,
            "is_available": self.is_available
        }
