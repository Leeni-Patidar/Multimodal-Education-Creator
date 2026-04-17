"""
Vector database retrieval operations.
Handles similarity search and context retrieval from ChromaDB.
"""

import logging
from typing import List, Dict, Tuple
from vector_db.db import get_vector_db

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieves relevant documents from vector database based on query similarity."""
    
    def __init__(self, top_k: int = 3):
        """
        Initialize the retriever.
        
        Args:
            top_k: Number of top documents to retrieve
        """
        self.top_k = top_k
        self.db = get_vector_db()

    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve top-k most similar documents for a query.
        
        Args:
            query: Query string
            top_k: Override default top_k for this retrieval
        
        Returns:
            List of retrieved documents with metadata
        """
        k = top_k or self.top_k
        
        try:
            logger.info(f"Retrieving top-{k} documents for query: {query[:100]}...")
            
            collection = self.db.collection
            
            # Query the collection - ChromaDB handles embedding the query internally
            results = collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            retrieved_docs = []
            if results and results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else None
                    similarity_score = 1 - distance if distance is not None else None
                    
                    retrieved_docs.append({
                        "content": doc,
                        "title": metadata.get("title", "Unknown"),
                        "category": metadata.get("category", "General"),
                        "level": metadata.get("level", "beginner"),
                        "similarity_score": similarity_score,
                        "distance": distance
                    })
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            for i, doc in enumerate(retrieved_docs):
                logger.debug(f"  [{i+1}] {doc['title']} (similarity: {doc['similarity_score']:.3f})")
            
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []

    def retrieve_and_format(self, query: str, top_k: int = None, include_scores: bool = False) -> str:
        """
        Retrieve documents and format them as a context string for LLM.
        
        Args:
            query: Query string
            top_k: Override default top_k
            include_scores: Include similarity scores in output
        
        Returns:
            Formatted context string
        """
        docs = self.retrieve(query, top_k)
        
        if not docs:
            return "No relevant documents found in knowledge base."
        
        context_parts = ["# Retrieved Context\n"]
        
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"## Document {i}: {doc['title']}")
            if include_scores:
                context_parts.append(f"(Relevance: {doc['similarity_score']:.1%}, Category: {doc['category']}, Level: {doc['level']})")
            context_parts.append(f"\n{doc['content']}\n")
        
        return "\n".join(context_parts)

    def retrieve_by_category(self, query: str, category: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve documents filtered by category.
        Note: Filtering happens client-side as ChromaDB's where clause is limited.
        
        Args:
            query: Query string
            category: Filter by category
            top_k: Override default top_k (applied before filtering)
        
        Returns:
            Filtered list of retrieved documents
        """
        k = top_k or self.top_k * 2  # Get more to filter
        docs = self.retrieve(query, k)
        
        filtered_docs = [doc for doc in docs if doc["category"].lower() == category.lower()]
        return filtered_docs[:self.top_k]

    def retrieve_by_level(self, query: str, level: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve documents filtered by difficulty level.
        
        Args:
            query: Query string
            level: Difficulty level (beginner, intermediate, advanced)
            top_k: Override default top_k
        
        Returns:
            Filtered list of retrieved documents
        """
        k = top_k or self.top_k * 2
        docs = self.retrieve(query, k)
        
        filtered_docs = [doc for doc in docs if doc["level"].lower() == level.lower()]
        return filtered_docs[:self.top_k]


# Convenience function for quick retrieval
def quick_retrieve(query: str, top_k: int = 3) -> List[Dict]:
    """
    Quick retrieval function without instantiating retriever class.
    
    Args:
        query: Query string
        top_k: Number of documents to retrieve
    
    Returns:
        List of retrieved documents
    """
    retriever = DocumentRetriever(top_k=top_k)
    return retriever.retrieve(query)


def quick_retrieve_formatted(query: str, top_k: int = 3) -> str:
    """
    Quick retrieval with formatted output.
    
    Args:
        query: Query string
        top_k: Number of documents to retrieve
    
    Returns:
        Formatted context string
    """
    retriever = DocumentRetriever(top_k=top_k)
    return retriever.retrieve_and_format(query, top_k)
