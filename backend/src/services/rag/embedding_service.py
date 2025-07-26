from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import tiktoken
from ...utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        
    async def initialize(self):
        """Initialize embedding model"""
        try:
            # Use a good multilingual model for embeddings
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            logger.info("Embedding service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks for processing"""
        if not self.tokenizer:
            # Fallback to character-based chunking
            chunks = []
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
            return chunks
        
        # Token-based chunking
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            if chunk_text.strip():
                chunks.append(chunk_text)
                
        return chunks
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for text chunks"""
        try:
            if not self.model:
                await self.initialize()
            
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            return []
    
    async def process_document_text(
        self, 
        text: str, 
        document_id: str,
        filename: str
    ) -> Dict[str, Any]:
        """Process document text into chunks and embeddings"""
        try:
            # Split into chunks
            chunks = self.chunk_text(text)
            
            if not chunks:
                return {"success": False, "error": "No text chunks generated"}
            
            # Create embeddings (ChromaDB will handle this automatically)
            # We just need to prepare the data
            
            chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": i,
                    "chunk_count": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            return {
                "success": True,
                "chunks": chunks,
                "chunk_ids": chunk_ids,
                "metadatas": metadatas,
                "chunk_count": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Failed to process document text: {e}")
            return {"success": False, "error": str(e)}


# Global embedding service instance
embedding_service = EmbeddingService()
