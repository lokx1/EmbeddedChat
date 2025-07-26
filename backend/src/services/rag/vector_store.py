import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from ...core.config import settings
from ...utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        
    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.getcwd(), "data", "chroma")
            os.makedirs(data_dir, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=data_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection("documents")
                logger.info("Using existing ChromaDB collection")
            except:
                self.collection = self.client.create_collection(
                    name="documents",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Created new ChromaDB collection")
                
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str]
    ) -> bool:
        """Add documents to vector store"""
        try:
            if not self.collection:
                await self.initialize()
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    async def search_similar(
        self, 
        query: str, 
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents"""
        try:
            if not self.collection:
                await self.initialize()
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector store"""
        try:
            if not self.collection:
                await self.initialize()
            
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document {doc_id} from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            if not self.collection:
                await self.initialize()
            
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "documents"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"total_documents": 0, "collection_name": "documents"}


# Global vector store instance
vector_store = VectorStore()
