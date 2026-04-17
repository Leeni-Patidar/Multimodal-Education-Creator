"""
Bonus: Store generated responses back into ChromaDB for future retrieval.
This enables continuous learning and knowledge accumulation.
"""

import logging
from typing import Optional
from datetime import datetime
from uuid import uuid4
from vector_db.db import get_vector_db

logger = logging.getLogger(__name__)


def store_generated_response(
    query: str,
    topic: str,
    generated_text: str,
    category: str = "Generated",
    level: str = "intermediate",
    metadata_context: Optional[dict] = None
) -> str:
    """
    Store a generated LLM response back into ChromaDB for future retrieval.
    
    This enables:
    - Continuous learning from generated content
    - Reusing high-quality responses
    - Building up domain-specific knowledge over time
    
    Args:
        query: Original user query
        topic: Topic being discussed
        generated_text: The LLM-generated response
        category: Content category (default: Generated)
        level: Difficulty level
        metadata_context: Optional retrieval metadata
    
    Returns:
        Document ID of stored response
    """
    try:
        db = get_vector_db()
        collection = db.collection
        
        # Create document ID
        doc_id = str(uuid4())
        
        # Enhance generated text with metadata
        enhanced_content = f"{generated_text}\n\n[Generated for: {query}]"
        
        # Build metadata
        metadata = {
            "title": f"Generated: {topic}",
            "category": category,
            "level": level,
            "source": "generated",
            "timestamp": datetime.now().isoformat(),
            "original_query": query[:200],  # Limit size
        }
        
        # Add retrieval context if available
        if metadata_context:
            metadata["used_documents"] = ",".join(
                metadata_context.get("retrieved_titles", [])[:3]
            )
            metadata["avg_similarity"] = str(
                metadata_context.get("avg_similarity_score", 0)
            )
        
        # Store in ChromaDB
        collection.add(
            documents=[enhanced_content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        logger.info(f"Stored generated response with ID: {doc_id}, Topic: {topic}")
        return doc_id
        
    except Exception as e:
        logger.error(f"Error storing generated response: {str(e)}")
        raise


def store_batch_responses(responses: list) -> list:
    """
    Store multiple generated responses in batch.
    
    Args:
        responses: List of dicts with keys:
            - query: Original query
            - topic: Topic
            - generated_text: Generated response
            - category: (optional) Category
            - level: (optional) Level
    
    Returns:
        List of document IDs
    """
    doc_ids = []
    for response in responses:
        try:
            doc_id = store_generated_response(
                query=response["query"],
                topic=response["topic"],
                generated_text=response["generated_text"],
                category=response.get("category", "Generated"),
                level=response.get("level", "intermediate"),
                metadata_context=response.get("metadata_context")
            )
            doc_ids.append(doc_id)
        except Exception as e:
            logger.error(f"Error storing response for {response.get('topic')}: {str(e)}")
    
    logger.info(f"Stored {len(doc_ids)} batch responses")
    return doc_ids


def get_generated_content_by_topic(topic: str, top_k: int = 3) -> list:
    """
    Retrieve previously generated content for a topic.
    
    Args:
        topic: Topic to search for
        top_k: Number of results
    
    Returns:
        List of generated content documents
    """
    from vector_db.retriever import DocumentRetriever
    
    retriever = DocumentRetriever(top_k=top_k)
    docs = retriever.retrieve(topic)
    
    # Filter generated content
    generated_docs = [d for d in docs if d.get("category") == "Generated"]
    
    logger.info(f"Retrieved {len(generated_docs)} generated responses for {topic}")
    return generated_docs


def cleanup_old_responses(max_count: int = 1000):
    """
    Cleanup old generated responses to manage database size.
    This is a simple count-based cleanup.
    
    Args:
        max_count: Maximum documents to keep
    """
    try:
        db = get_vector_db()
        collection = db.collection
        
        total_count = collection.count()
        if total_count > max_count:
            logger.warning(f"Database has {total_count} documents, exceeds limit of {max_count}")
            logger.warning("Consider resetting or implementing time-based cleanup")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


# Example usage in routes (integrate into generate.py if desired)
"""
# In routes/generate.py after successful generation:

if RAG_ENABLED and response.get("explanation"):
    try:
        from utils.response_storage import store_generated_response
        
        doc_id = store_generated_response(
            query=req.topic,
            topic=req.topic,
            generated_text=response["explanation"],
            level=req.level,
            metadata_context=rag_context.get("text_retrieval") if rag_context else None
        )
        response["stored_response_id"] = doc_id
        logger.info(f"Generated response stored with ID: {doc_id}")
    except Exception as e:
        logger.warning(f"Could not store response: {str(e)}")
"""
