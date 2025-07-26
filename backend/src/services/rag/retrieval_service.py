from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...models.document import Document
from .vector_store import vector_store
from ...utils.logger import get_logger

logger = get_logger(__name__)


class RetrievalService:
    """Handle document retrieval logic for RAG (Retrieval-Augmented Generation)"""
    
    async def search_documents(
        self, 
        query: str, 
        user_id: int,
        db: AsyncSession,
        max_results: int = 5,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Search for relevant document chunks"""
        try:
            # Search in vector store
            search_results = await vector_store.search_similar(
                query=query,
                n_results=max_results,
                where={"user_id": str(user_id)}  # Filter by user
            )
            
            if not search_results["documents"]:
                return {
                    "success": True,
                    "results": [],
                    "context": ""
                }
            
            # Filter by similarity threshold
            filtered_results = []
            for i, distance in enumerate(search_results["distances"]):
                # Convert distance to similarity (ChromaDB uses cosine distance)
                similarity = 1 - distance
                if similarity >= similarity_threshold:
                    filtered_results.append({
                        "text": search_results["documents"][i],
                        "metadata": search_results["metadatas"][i],
                        "similarity": similarity,
                        "chunk_id": search_results["ids"][i]
                    })
            
            # Create context string for LLM
            context_parts = []
            for result in filtered_results:
                metadata = result["metadata"]
                context_parts.append(
                    f"[Document: {metadata.get('filename', 'Unknown')}]\n{result['text']}\n"
                )
            
            context = "\n---\n".join(context_parts)
            
            return {
                "success": True,
                "results": filtered_results,
                "context": context,
                "total_chunks": len(filtered_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "context": ""
            }
    
    async def get_document_context(
        self, 
        document_id: int, 
        user_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get all chunks from a specific document"""
        try:
            # Verify document belongs to user
            result = await db.execute(
                select(Document).where(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            )
            document = result.scalar_one_or_none()
            
            if not document:
                return {
                    "success": False,
                    "error": "Document not found or access denied"
                }
            
            # Get all chunks for this document
            search_results = await vector_store.search_similar(
                query="",  # Empty query to get all
                n_results=1000,  # Get all chunks
                where={"document_id": str(document_id)}
            )
            
            chunks = []
            for i, chunk_text in enumerate(search_results["documents"]):
                chunks.append({
                    "text": chunk_text,
                    "metadata": search_results["metadatas"][i],
                    "chunk_id": search_results["ids"][i]
                })
            
            return {
                "success": True,
                "document": {
                    "id": document.id,
                    "filename": document.original_filename,
                    "summary": document.summary
                },
                "chunks": chunks,
                "total_chunks": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Failed to get document context: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_related_documents(
        self, 
        document_id: int, 
        user_id: int,
        db: AsyncSession,
        max_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Find documents related to the given document"""
        try:
            # Get the document's summary or first chunk as query
            result = await db.execute(
                select(Document).where(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            )
            document = result.scalar_one_or_none()
            
            if not document:
                return []
            
            query_text = document.summary or "related documents"
            
            # Search for similar documents
            search_results = await vector_store.search_similar(
                query=query_text,
                n_results=max_results + 1,  # +1 to exclude the original document
                where={"user_id": str(user_id)}
            )
            
            # Filter out the original document and group by document_id
            related_docs = {}
            for i, metadata in enumerate(search_results["metadatas"]):
                doc_id = metadata.get("document_id")
                if doc_id and doc_id != str(document_id):
                    if doc_id not in related_docs:
                        related_docs[doc_id] = {
                            "document_id": doc_id,
                            "filename": metadata.get("filename", "Unknown"),
                            "relevance_score": 1 - search_results["distances"][i]
                        }
            
            # Return top related documents
            return list(related_docs.values())[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to get related documents: {e}")
            return []


# Global retrieval service instance
retrieval_service = RetrievalService()
