"""
ChromaDB initialization and management.
Handles persistent vector database connections and collection management.
"""

import os
import logging
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

# Get ChromaDB persistence directory
CHROMADB_DIR = os.getenv("CHROMADB_DIR", "./chroma_data")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "educational_content")


class VectorDB:
    """Singleton vector database manager for ChromaDB operations."""
    
    _instance = None
    _client = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, persist_dir: str = CHROMADB_DIR, collection_name: str = COLLECTION_NAME):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            persist_dir: Directory to persist ChromaDB data
            collection_name: Name of the collection to use
        """
        if self._initialized and self._client is not None:
            logger.info("VectorDB already initialized")
            return

        try:
            os.makedirs(persist_dir, exist_ok=True)
            logger.info(f"Initializing ChromaDB with persistence directory: {persist_dir}")
            
            # Create ChromaDB client with persistence
            self._client = chromadb.PersistentClient(path=persist_dir)
            
            # Get or create collection with sentence-transformers embedding function
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
                # Using default embedding function (sentence-transformers)
            )
            
            self._initialized = True
            logger.info(f"ChromaDB initialized successfully with collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise

    @property
    def client(self):
        """Get ChromaDB client."""
        if self._client is None:
            self.initialize()
        return self._client

    @property
    def collection(self):
        """Get ChromaDB collection."""
        if self._collection is None:
            self.initialize()
        return self._collection

    def get_collection_stats(self) -> dict:
        """Get statistics about the collection."""
        try:
            collection = self.collection
            stats = {
                "count": collection.count(),
                "name": collection.name,
                "metadata": collection.metadata,
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}

    def reset_collection(self, collection_name: str = COLLECTION_NAME):
        """Reset/delete and recreate collection (useful for testing)."""
        try:
            logger.warning(f"Resetting collection: {collection_name}")
            self._client.delete_collection(name=collection_name)
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Collection reset successfully")
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise


# Singleton instance
def get_vector_db() -> VectorDB:
    """Get or create VectorDB singleton instance."""
    return VectorDB()
