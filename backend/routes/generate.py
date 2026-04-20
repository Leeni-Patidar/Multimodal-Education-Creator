import base64
import logging
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.schema import GenerateRequest
from services.image_service import generate_images
from services.llm_service import generate_text
from utils.prompt_builder import build_image_prompt, build_text_prompt
from rag.pipeline import build_rag_prompt, build_enhanced_image_prompt
from vector_db.ingest import ingest_sample_content
from vector_db.db import get_vector_db

router = APIRouter()
logger = logging.getLogger(__name__)

# Thread pool for blocking I/O operations
executor = ThreadPoolExecutor(max_workers=2)

# Configuration
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
INGEST_ON_STARTUP = os.getenv("INGEST_ON_STARTUP", "true").lower() == "true"

# Initialize vector DB on startup
def _initialize_vector_db():
    """Initialize ChromaDB and ingest sample content if needed."""
    try:
        db = get_vector_db()
        db.initialize()
        if INGEST_ON_STARTUP:
            ingest_sample_content()
        logger.info("Vector DB initialized successfully")
    except Exception as e:
        logger.warning(f"Vector DB initialization warning: {str(e)}")


@router.post("/generate")
async def generate_content(req: GenerateRequest):
    try:
        logger.info(f"Generating content for topic: {req.topic}, RAG enabled: {RAG_ENABLED}")
        
        # Initialize vector DB on first request
        _initialize_vector_db()

        # Stage 1: Build prompts
        if RAG_ENABLED:
            logger.info("Building prompts with RAG enhancement...")
            # Build text prompt with RAG context
            text_prompt, text_metadata = build_rag_prompt(
                user_query=req.topic,
                topic=req.topic,
                level=req.level,
                top_k=3,
                use_context=True
            )
            
            # Build image prompt with RAG context
            image_prompt_enhanced, image_metadata = build_enhanced_image_prompt(
                user_query=req.topic,
                image_prompt=req.image_prompt,
                style=req.style,
                top_k=2
            )
            
            rag_context = {
                "text_retrieval": text_metadata,
                "image_retrieval": image_metadata
            }
        else:
            logger.info("Building prompts without RAG...")
            text_prompt = build_text_prompt(req.topic, req.level)
            image_topic = req.image_prompt.strip() if req.image_prompt and req.image_prompt.strip() else req.topic
            image_prompt_enhanced = build_image_prompt(image_topic, req.style)
            text_metadata = None
            rag_context = None

        # Stage 2: Run text and image generation in parallel
        logger.info("Starting parallel content generation...")
        loop = asyncio.get_event_loop()
        
        text_output, image_bytes_list = await asyncio.gather(
            loop.run_in_executor(executor, generate_text, text_prompt, text_metadata),
            loop.run_in_executor(executor, generate_images, image_prompt_enhanced, req.image_count),
            return_exceptions=True
        )
        
        # Handle exceptions from gather
        if isinstance(text_output, Exception):
            logger.error(f"Text generation error: {str(text_output)}")
            text_output = f"Error generating text: {str(text_output)}"
        
        if isinstance(image_bytes_list, Exception):
            logger.error(f"Image generation error: {str(image_bytes_list)}")
            image_bytes_list = []

        images_base64 = [
            base64.b64encode(image_bytes).decode("utf-8")
            for image_bytes in image_bytes_list
            if image_bytes
        ]

        logger.info("Content generation completed successfully")
        
        response = {
            "topic": req.topic,
            "explanation": text_output,
            "image": images_base64[0] if images_base64 else None,
            "images": images_base64,
        }
        
        # Include RAG metadata in response
        if RAG_ENABLED and rag_context:
            response["rag_context"] = rag_context
        
        # Store generated response in vector DB for history
        try:
            from utils.response_storage import store_generated_response
            
            doc_id = store_generated_response(
                query=req.topic,
                topic=req.topic,
                generated_text=text_output,
                level=req.level,
                metadata_context=rag_context.get("text_retrieval") if rag_context else None
            )
            response["stored_response_id"] = doc_id
            logger.info(f"Generated response stored with ID: {doc_id}")
        except Exception as e:
            logger.warning(f"Could not store response to history: {str(e)}")
        
        return response
        
    except Exception as e:
        logger.exception(f"Error generating content: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to generate content"},
        )


@router.post("/ingest")
async def ingest_data():
    """
    Manually trigger data ingestion into vector database.
    Useful for reinitializing the content.
    """
    try:
        logger.info("Manual data ingestion triggered")
        db = get_vector_db()
        db.initialize()
        
        # Reset collection for fresh ingestion
        db.reset_collection()
        count = ingest_sample_content()
        
        return {
            "status": "success",
            "message": f"Ingested {count} documents",
            "ingested_count": count
        }
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Ingestion failed"},
        )


@router.get("/vector-db/stats")
async def get_vector_db_stats():
    """Get vector database statistics."""
    try:
        db = get_vector_db()
        stats = db.get_collection_stats()
        return {
            "status": "success",
            "stats": stats,
            "rag_enabled": RAG_ENABLED
        }
    except Exception as e:
        logger.error(f"Error getting vector DB stats: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to get stats"},
        )


@router.get("/history")
async def get_history(limit: int = 10):
    """
    Get recent generated content history from vector database.
    
    Args:
        limit: Number of recent items to retrieve
    
    Returns:
        List of recent generation records
    """
    try:
        from vector_db.retriever import DocumentRetriever
        
        logger.info(f"Retrieving history (limit: {limit})")
        
        db = get_vector_db()
        collection = db.collection
        
        # Fetch more items than needed to filter and sort properly
        fetch_limit = limit * 5
        results = collection.get(
            limit=fetch_limit,
            include=["documents", "metadatas"]
        )
        
        history_items = []
        if results and results.get("metadatas"):
            for i, metadata in enumerate(results["metadatas"]):
                if metadata.get("source") == "generated":
                    history_items.append({
                        "id": results["ids"][i] if results.get("ids") else None,
                        "title": metadata.get("title", "Unknown"),
                        "topic": metadata.get("original_query", ""),
                        "category": metadata.get("category", "Generated"),
                        "level": metadata.get("level", "intermediate"),
                        "timestamp": metadata.get("timestamp", ""),
                        "content_preview": results["documents"][i][:200] if results.get("documents") else ""
                    })
        
        # Sort by timestamp (most recent first)
        history_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Deduplicate by topic - keep only the most recent occurrence of each topic
        seen_topics = set()
        deduplicated_items = []
        for item in history_items:
            topic = item.get("topic", "").lower().strip()
            if topic and topic not in seen_topics:
                seen_topics.add(topic)
                deduplicated_items.append(item)
        
        # Return only the requested limit
        deduplicated_items = deduplicated_items[:limit]
        
        logger.info(f"Retrieved {len(deduplicated_items)} unique history items (deduped from {len(history_items)})")
        return {
            "status": "success",
            "history": deduplicated_items,
            "total_count": len(deduplicated_items)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to retrieve history"},
        )


@router.get("/history/search")
async def search_history(query: str = "", category: str = "", level: str = "", limit: int = 10):
    """
    Search generated content history with optional filters.
    
    Args:
        query: Search query/topic
        category: Filter by category
        level: Filter by level (beginner, intermediate, advanced)
        limit: Maximum results to return
    
    Returns:
        List of matching history items
    """
    try:
        from vector_db.retriever import DocumentRetriever
        
        logger.info(f"Searching history: query='{query}', category='{category}', level='{level}'")
        
        if not query:
            # If no query, return all recent
            return await get_history(limit)
        
        retriever = DocumentRetriever(top_k=limit)
        docs = retriever.retrieve(query)
        
        # Filter for generated content only
        history_items = []
        for doc in docs:
            # Apply category filter
            if category and doc.get("category", "").lower() != category.lower():
                continue
            
            # Apply level filter
            if level and doc.get("level", "").lower() != level.lower():
                continue
            
            history_items.append({
                "title": doc.get("title", "Unknown"),
                "topic": query,
                "category": doc.get("category", "Generated"),
                "level": doc.get("level", "intermediate"),
                "similarity_score": doc.get("similarity_score", 0),
                "content_preview": doc.get("content", "")[:200]
            })
        
        logger.info(f"Found {len(history_items)} matching history items")
        return {
            "status": "success",
            "history": history_items[:limit],
            "search_query": query,
            "filters": {
                "category": category or None,
                "level": level or None
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching history: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to search history"},
        )
