#!/usr/bin/env python3
"""
Initialize document system and create sample documents for testing
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from src.models.database import AsyncSessionLocal
from src.models.document import Document, DocumentStatus
from src.services.rag.vector_store import vector_store
from src.services.rag.embedding_service import embedding_service
from src.services.document.storage_service import storage_service

async def get_async_session():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        yield session

async def init_vector_store():
    """Initialize the vector store"""
    print("🔧 Initializing vector store...")
    try:
        await vector_store.initialize()
        print("✅ Vector store initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize vector store: {e}")
        return False
    return True

async def init_embedding_service():
    """Initialize the embedding service"""
    print("🔧 Initializing embedding service...")
    try:
        await embedding_service.initialize()
        print("✅ Embedding service initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize embedding service: {e}")
        return False
    return True

async def create_sample_documents():
    """Create sample text documents for testing"""
    print("📄 Creating sample documents...")
    
    sample_docs = [
        {
            "filename": "getting_started.txt",
            "content": """Getting Started with EmbeddedChat

Welcome to EmbeddedChat, an advanced chatbot platform with document processing capabilities.

Key Features:
- Real-time chat with AI assistance
- Document upload and processing
- Semantic search across documents
- Vector-based retrieval augmented generation (RAG)
- User authentication and session management

To get started:
1. Register an account or log in
2. Upload your documents in the Documents section
3. Start chatting and ask questions about your documents
4. The AI will search your documents and provide contextual answers

Supported document formats:
- PDF files
- Microsoft Word documents
- Excel spreadsheets
- Plain text files
- CSV files

The system automatically processes uploaded documents, extracts text content, and creates vector embeddings for semantic search."""
        },
        {
            "filename": "technical_overview.txt", 
            "content": """Technical Architecture Overview

EmbeddedChat is built with modern technologies for scalability and performance:

Backend Stack:
- FastAPI: High-performance web framework
- SQLAlchemy: Async ORM for database operations
- ChromaDB: Vector database for document embeddings
- Sentence Transformers: Text embedding generation
- PostgreSQL: Primary database for structured data

Frontend Stack:
- React: Component-based UI framework
- TypeScript: Type-safe JavaScript development
- Tailwind CSS: Utility-first CSS framework
- Vite: Fast build tool and development server

Key Components:
1. Document Processing Pipeline
   - File upload and validation
   - Text extraction from various formats
   - Content chunking for optimal retrieval
   - Vector embedding generation
   - Storage in both SQL and vector databases

2. RAG (Retrieval Augmented Generation)
   - Semantic search across document chunks
   - Context retrieval for AI responses
   - Relevance scoring and filtering
   - Multi-document context aggregation

3. Real-time Features
   - WebSocket connections for live chat
   - Background document processing
   - Real-time status updates
   - Live typing indicators

Security Features:
- JWT-based authentication
- Role-based access control
- File type validation
- Size limits and rate limiting
- CORS protection"""
        },
        {
            "filename": "api_documentation.txt",
            "content": """API Documentation

Authentication Endpoints:
POST /api/v1/auth/register - Register new user
POST /api/v1/auth/login - User login
POST /api/v1/auth/login-json - JSON-based login
GET /api/v1/auth/me - Get current user info

Document Management:
POST /api/v1/documents/upload - Upload document
GET /api/v1/documents/ - List user documents
DELETE /api/v1/documents/{id} - Delete document
POST /api/v1/documents/search - Search documents
GET /api/v1/documents/{id}/context - Get document chunks
GET /api/v1/documents/{id}/related - Find related documents
GET /api/v1/documents/stats - Document statistics

Chat Endpoints:
GET /api/v1/chat/conversations - List conversations
POST /api/v1/chat/conversations - Create conversation
GET /api/v1/chat/conversations/{id} - Get conversation
DELETE /api/v1/chat/conversations/{id} - Delete conversation
POST /api/v1/chat/conversations/{id}/messages - Send message
WebSocket /api/v1/chat/ws/{conversation_id} - Real-time chat

Dashboard Analytics:
GET /api/v1/dashboard/stats/overview - Overview statistics
GET /api/v1/dashboard/stats/chat - Chat analytics
GET /api/v1/dashboard/stats/user - User analytics
GET /api/v1/dashboard/stats/document - Document statistics
GET /api/v1/dashboard/stats/system - System performance

Error Handling:
All endpoints return standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

Rate Limiting:
- Authentication: 10 requests per minute
- Document upload: 5 requests per minute
- Chat messages: 60 requests per minute
- Search queries: 30 requests per minute"""
        }
    ]
    
    # Create data directory
    upload_dir = Path("data/uploads/system")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    created_docs = []
    
    for doc_data in sample_docs:
        file_path = upload_dir / doc_data["filename"]
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(doc_data["content"])
        
        created_docs.append({
            "filename": doc_data["filename"],
            "file_path": str(file_path),
            "content": doc_data["content"],
            "size": len(doc_data["content"].encode('utf-8'))
        })
        
        print(f"📝 Created {doc_data['filename']}")
    
    return created_docs

async def process_sample_documents(sample_docs):
    """Process sample documents and add to vector store"""
    print("🔄 Processing sample documents...")
    
    async for session in get_async_session():
        try:
            for doc_data in sample_docs:
                # Create database record
                document = Document(
                    filename=doc_data["filename"],
                    original_filename=doc_data["filename"],
                    file_path=doc_data["file_path"],
                    file_size=doc_data["size"],
                    mime_type="text/plain",
                    user_id=1,  # System user
                    status=DocumentStatus.PROCESSING,
                    extracted_text=doc_data["content"]
                )
                
                session.add(document)
                await session.commit()
                await session.refresh(document)
                
                # Process text for vector storage
                process_result = await embedding_service.process_document_text(
                    doc_data["content"],
                    str(document.id),
                    document.filename
                )
                
                if process_result["success"]:
                    # Add to vector store
                    vector_result = await vector_store.add_documents(
                        documents=process_result["chunks"],
                        metadatas=process_result["metadatas"],
                        ids=process_result["chunk_ids"]
                    )
                    
                    if vector_result:
                        document.status = DocumentStatus.READY
                        document.chunk_count = process_result["chunk_count"]
                        document.embedding_model = "all-MiniLM-L6-v2"
                        document.summary = doc_data["content"][:500] + "..."
                        
                        await session.commit()
                        print(f"✅ Processed {document.filename} ({document.chunk_count} chunks)")
                    else:
                        document.status = DocumentStatus.ERROR
                        document.error_message = "Failed to store in vector database"
                        await session.commit()
                        print(f"❌ Failed to store {document.filename} in vector database")
                else:
                    document.status = DocumentStatus.ERROR
                    document.error_message = process_result["error"]
                    await session.commit()
                    print(f"❌ Failed to process {document.filename}: {process_result['error']}")
                    
        except Exception as e:
            print(f"❌ Error processing documents: {e}")
            await session.rollback()
        finally:
            await session.close()

async def test_vector_search():
    """Test vector search functionality"""
    print("🔍 Testing vector search...")
    
    test_queries = [
        "How do I get started?",
        "What technologies are used?",
        "API documentation",
        "document upload"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = await vector_store.search_similar(query, n_results=2)
        
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                distance = results["distances"][i]
                similarity = 1 - distance
                
                print(f"  📄 {metadata.get('filename', 'Unknown')} (similarity: {similarity:.3f})")
                print(f"     {doc[:100]}...")
        else:
            print("  ❌ No results found")

async def main():
    """Main initialization function"""
    print("🚀 Initializing EmbeddedChat Document System")
    print("=" * 50)
    
    # Initialize services
    if not await init_vector_store():
        return
    
    if not await init_embedding_service():
        return
    
    # Create and process sample documents
    sample_docs = await create_sample_documents()
    await process_sample_documents(sample_docs)
    
    # Test search functionality
    await test_vector_search()
    
    # Get statistics
    stats = await vector_store.get_collection_stats()
    print(f"\n📊 Vector Store Statistics:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    
    print("\n✅ Document system initialization completed!")
    print("You can now:")
    print("- Start the backend server: python main.py")
    print("- Upload documents via the API")
    print("- Search documents using semantic search")

if __name__ == "__main__":
    asyncio.run(main())
