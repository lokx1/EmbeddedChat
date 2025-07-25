# Create a comprehensive file structure for the EmbeddedChat application
import json

embedded_chat_structure = {
    "EmbeddedChat": {
        "backend/": {
            "src/": {
                "core/": {
                    "__init__.py": "# Core application module",
                    "config.py": "# Application configuration",
                    "exceptions.py": "# Custom exceptions",
                    "base.py": "# Base classes and interfaces"
                },
                "api/": {
                    "__init__.py": "",
                    "routes/": {
                        "__init__.py": "",
                        "chat.py": "# Chat endpoints",
                        "documents.py": "# Document upload/management endpoints", 
                        "health.py": "# Health check endpoints",
                        "ai.py": "# AI/Ollama integration endpoints"
                    },
                    "middleware/": {
                        "__init__.py": "",
                        "cors.py": "# CORS middleware",
                        "auth.py": "# Authentication middleware",
                        "rate_limiting.py": "# Rate limiting middleware"
                    },
                    "schemas/": {
                        "__init__.py": "",
                        "chat.py": "# Chat message schemas",
                        "document.py": "# Document schemas",
                        "user.py": "# User schemas"
                    }
                },
                "services/": {
                    "__init__.py": "",
                    "ai/": {
                        "__init__.py": "",
                        "ollama_client.py": "# Ollama API client",
                        "prompt_manager.py": "# Prompt templates and management",
                        "response_processor.py": "# AI response processing"
                    },
                    "rag/": {
                        "__init__.py": "",
                        "document_processor.py": "# PDF processing and chunking",
                        "embedding_service.py": "# Text embedding generation",
                        "retrieval_service.py": "# Document retrieval logic",
                        "vector_store.py": "# Vector database operations"
                    },
                    "chat/": {
                        "__init__.py": "",
                        "message_handler.py": "# Message processing logic",
                        "conversation_manager.py": "# Conversation state management",
                        "websocket_manager.py": "# WebSocket connection management"
                    },
                    "document/": {
                        "__init__.py": "",
                        "upload_service.py": "# File upload handling",
                        "storage_service.py": "# Document storage management",
                        "validation_service.py": "# Document validation"
                    }
                },
                "models/": {
                    "__init__.py": "",
                    "database.py": "# Database connection and base model",
                    "conversation.py": "# Conversation model",
                    "message.py": "# Message model",
                    "document.py": "# Document model",
                    "user.py": "# User model"
                },
                "utils/": {
                    "__init__.py": "",
                    "file_utils.py": "# File handling utilities",
                    "text_utils.py": "# Text processing utilities",
                    "vector_utils.py": "# Vector operations utilities",
                    "logger.py": "# Logging configuration"
                },
                "plugins/": {
                    "__init__.py": "",
                    "base_plugin.py": "# Base plugin interface",
                    "registry.py": "# Plugin registry",
                    "loader.py": "# Plugin loader",
                    "examples/": {
                        "__init__.py": "",
                        "translation_plugin.py": "# Example translation plugin",
                        "summarization_plugin.py": "# Example summarization plugin"
                    }
                }
            },
            "tests/": {
                "__init__.py": "",
                "unit/": {
                    "test_services.py": "# Unit tests for services",
                    "test_models.py": "# Unit tests for models",
                    "test_utils.py": "# Unit tests for utilities"
                },
                "integration/": {
                    "test_api.py": "# API integration tests",
                    "test_ollama.py": "# Ollama integration tests"
                },
                "fixtures/": {
                    "sample_documents.py": "# Test document fixtures"
                }
            },
            "requirements.txt": "# Python dependencies",
            "Dockerfile": "# Docker configuration",
            "docker-compose.yml": "# Docker compose for development",
            "main.py": "# Application entry point",
            "alembic.ini": "# Database migration config",
            "migrations/": {
                "versions/": {}
            }
        },
        "frontend/": {
            "src/": {
                "components/": {
                    "Chat/": {
                        "index.ts": "# Chat component exports",
                        "ChatContainer.tsx": "# Main chat container",
                        "MessageList.tsx": "# Message list component",
                        "MessageInput.tsx": "# Message input component",
                        "MessageBubble.tsx": "# Individual message bubble",
                        "TypingIndicator.tsx": "# Typing indicator",
                        "FileUpload.tsx": "# File upload in chat"
                    },
                    "DocumentManager/": {
                        "index.ts": "",
                        "DocumentList.tsx": "# Document list viewer",
                        "DocumentUpload.tsx": "# Document upload component",
                        "DocumentViewer.tsx": "# PDF viewer component",
                        "DocumentCard.tsx": "# Document card component"
                    },
                    "UI/": {
                        "index.ts": "",
                        "Button.tsx": "# Reusable button component",
                        "Input.tsx": "# Reusable input component",
                        "Modal.tsx": "# Modal component",
                        "Loader.tsx": "# Loading spinner",
                        "Toast.tsx": "# Toast notification"
                    },
                    "Layout/": {
                        "index.ts": "",
                        "Header.tsx": "# Application header",
                        "Sidebar.tsx": "# Navigation sidebar",
                        "Layout.tsx": "# Main layout wrapper"
                    }
                },
                "hooks/": {
                    "index.ts": "",
                    "useChat.ts": "# Chat functionality hook",
                    "useWebSocket.ts": "# WebSocket connection hook",
                    "useDocuments.ts": "# Document management hook",
                    "useApi.ts": "# API interaction hook"
                },
                "services/": {
                    "index.ts": "",
                    "api.ts": "# API client configuration",
                    "websocket.ts": "# WebSocket service",
                    "storage.ts": "# Local storage service"
                },
                "types/": {
                    "index.ts": "",
                    "chat.ts": "# Chat-related types",
                    "document.ts": "# Document-related types",
                    "api.ts": "# API response types"
                },
                "store/": {
                    "index.ts": "",
                    "chatSlice.ts": "# Chat state management",
                    "documentSlice.ts": "# Document state management",
                    "uiSlice.ts": "# UI state management"
                },
                "utils/": {
                    "index.ts": "",
                    "helpers.ts": "# Helper functions",
                    "constants.ts": "# Application constants",
                    "validation.ts": "# Form validation utilities"
                },
                "styles/": {
                    "globals.css": "# Global styles",
                    "components.css": "# Component-specific styles",
                    "chat.css": "# Chat interface styles",
                    "document.css": "# Document manager styles"
                }
            },
            "public/": {
                "index.html": "# Main HTML file",
                "favicon.ico": "# Application favicon",
                "manifest.json": "# PWA manifest",
                "icons/": {}
            },
            "package.json": "# Node.js dependencies",
            "tsconfig.json": "# TypeScript configuration",
            "vite.config.ts": "# Vite build configuration",
            "tailwind.config.js": "# Tailwind CSS configuration",
            "eslint.config.js": "# ESLint configuration"
        },
        "shared/": {
            "types/": {
                "api.ts": "# Shared API types",
                "models.ts": "# Shared data models"
            },
            "constants/": {
                "endpoints.ts": "# API endpoints",
                "messages.ts": "# Message constants"
            }
        },
        "docs/": {
            "README.md": "# Project documentation",
            "API.md": "# API documentation",
            "ARCHITECTURE.md": "# Architecture documentation",
            "DEPLOYMENT.md": "# Deployment guide",
            "PLUGINS.md": "# Plugin development guide"
        },
        "scripts/": {
            "setup.sh": "# Environment setup script",
            "start-dev.sh": "# Development startup script",
            "test.sh": "# Test execution script",
            "deploy.sh": "# Deployment script"
        },
        "docker-compose.yml": "# Full stack docker compose",
        "README.md": "# Main project README",
        ".gitignore": "# Git ignore file",
        ".env.example": "# Environment variables example"
    }
}

# Create a visual representation of the key modules and their relationships
modules_architecture = {
    "Core Modules": {
        "API Gateway": {
            "description": "FastAPI-based REST API and WebSocket handler",
            "responsibilities": [
                "HTTP request routing",
                "WebSocket connection management", 
                "Authentication & authorization",
                "Request/response validation",
                "CORS handling"
            ],
            "dependencies": ["Services Layer", "Models Layer"]
        },
        "RAG System": {
            "description": "Multimodal Retrieval-Augmented Generation system",
            "responsibilities": [
                "PDF document processing",
                "Text chunking and embedding",
                "Vector storage and retrieval",
                "Context augmentation for AI",
                "Multimodal content handling"
            ],
            "dependencies": ["Vector Database", "Embedding Service", "Document Processor"]
        },
        "AI Integration": {
            "description": "Ollama local AI model integration",
            "responsibilities": [
                "Model communication",
                "Prompt management",
                "Response processing",
                "Context handling",
                "Model switching capabilities"
            ],
            "dependencies": ["Ollama Server", "RAG System"]
        },
        "Chat Engine": {
            "description": "Real-time chat functionality",
            "responsibilities": [
                "Message routing",
                "Conversation management",
                "Real-time communication",
                "Message persistence",
                "User session handling"
            ],
            "dependencies": ["WebSocket Manager", "Database", "AI Integration"]
        },
        "Document Manager": {
            "description": "File upload and management system",
            "responsibilities": [
                "File upload handling",
                "Document validation",
                "Storage management",
                "Metadata extraction",
                "Document preprocessing"
            ],
            "dependencies": ["Storage Service", "RAG System"]
        },
        "Plugin System": {
            "description": "Extensible plugin architecture",
            "responsibilities": [
                "Plugin registration",
                "Dynamic loading",
                "Lifecycle management",
                "API provision",
                "Isolation and security"
            ],
            "dependencies": ["Plugin Registry", "Core Services"]
        }
    }
}

print("EmbeddedChat Application Architecture")
print("=====================================")
print()
print("File Structure:")
print(json.dumps(embedded_chat_structure, indent=2))
print()
print("Core Modules Architecture:")
print(json.dumps(modules_architecture, indent=2))