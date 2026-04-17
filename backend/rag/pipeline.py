"""
RAG (Retrieval-Augmented Generation) Pipeline.
Orchestrates document retrieval and prompt engineering for enhanced LLM responses.
"""

import logging
from typing import Dict, Tuple
from vector_db.retriever import DocumentRetriever, quick_retrieve_formatted

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG Pipeline that combines retrieval and generation stages.
    """
    
    def __init__(self, retrieval_top_k: int = 3, enable_detailed_logging: bool = False):
        """
        Initialize RAG pipeline.
        
        Args:
            retrieval_top_k: Number of documents to retrieve
            enable_detailed_logging: Enable detailed query/response logging
        """
        self.retrieval_top_k = retrieval_top_k
        self.enable_detailed_logging = enable_detailed_logging
        self.retriever = DocumentRetriever(top_k=retrieval_top_k)

    def process_query(self, user_query: str, topic: str, level: str = "basic") -> Tuple[str, Dict]:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            user_query: Original user question/topic
            topic: Educational topic
            level: Difficulty level
        
        Returns:
            Tuple of (enhanced_prompt, metadata)
        """
        try:
            logger.info(f"RAG Pipeline processing query: {user_query}")
            
            # Stage 1: Retrieve relevant documents
            retrieved_docs = self.retriever.retrieve(user_query, self.retrieval_top_k)
            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
            
            # Stage 2: Build context from retrieved documents
            context = self._build_context(retrieved_docs)
            
            # Stage 3: Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                user_query=user_query,
                topic=topic,
                level=level,
                context=context
            )
            
            # Stage 4: Collect metadata
            metadata = {
                "retrieved_docs_count": len(retrieved_docs),
                "retrieved_titles": [doc["title"] for doc in retrieved_docs],
                "avg_similarity_score": sum(doc.get("similarity_score", 0) for doc in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0,
                "rag_enabled": True,
                "retrieval_top_k": self.retrieval_top_k
            }
            
            if self.enable_detailed_logging:
                logger.debug(f"Enhanced prompt:\n{enhanced_prompt}")
                logger.debug(f"Metadata: {metadata}")
            
            return enhanced_prompt, metadata
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            # Fallback: return basic prompt without RAG
            return self._build_basic_prompt(user_query, topic, level), {"error": str(e), "rag_enabled": False}

    def _build_context(self, retrieved_docs: list) -> str:
        """Build context string from retrieved documents."""
        if not retrieved_docs:
            return ""
        
        context_parts = []
        for doc in retrieved_docs:
            context_parts.append(f"• {doc['title']}: {doc['content'][:300]}...")
        
        return "\n".join(context_parts)

    def _build_enhanced_prompt(self, user_query: str, topic: str, level: str, context: str) -> str:
        """
        Build an enhanced prompt with retrieved context.
        This prompt guides the LLM more effectively.
        """
        if not context:
            return self._build_basic_prompt(user_query, topic, level)
        
        prompt = f"""You are an expert educational content creator. Use the provided context to enhance your explanation.

CONTEXT FROM KNOWLEDGE BASE:
{context}

---

Now, explain the following using the context above when relevant:

Topic: {topic}
Difficulty Level: {level}
User Query: {user_query}

Format your response as:
**1. Definition** - Clear, concise definition
**2. Working** - How it works or the mechanism
**3. Examples** - Relevant examples (use context if available)
**4. Real-life Applications** - Practical uses
**5. Bullet Notes** - Key points summarized
**6. Step-by-step Explanation** - Detailed breakdown

Base your answer on the provided context, but you can enhance it with your knowledge. Be accurate and educational."""
        
        return prompt

    def _build_basic_prompt(self, user_query: str, topic: str, level: str) -> str:
        """Build a basic prompt when RAG context is unavailable."""
        prompt = f"""Explain the concept: {topic}

Difficulty Level: {level}
Query: {user_query}

Format:
**1. Definition**
**2. Working**
**3. Examples**
**4. Real-life applications**
**5. Bullet Notes**
**6. Step-by-step explanation**
"""
        return prompt

    def process_image_generation_query(self, user_query: str, image_prompt: str, style: str = "diagram") -> Tuple[str, Dict]:
        """
        Process query for image generation enhancement.
        
        Args:
            user_query: Original query
            image_prompt: User-provided image prompt
            style: Image style (diagram, illustration, etc)
        
        Returns:
            Tuple of (enhanced_image_prompt, metadata)
        """
        try:
            # Retrieve context for better image generation
            retrieved_docs = self.retriever.retrieve(user_query, top_k=2)
            
            # Extract context
            context_titles = [doc["title"] for doc in retrieved_docs]
            context_text = ". ".join(context_titles)
            
            # Enhance image prompt with context
            if image_prompt and image_prompt.strip():
                enhanced_image_prompt = f"{style} educational diagram of {image_prompt}. Related concepts: {context_text}. Clean, labeled, high quality, professional."
            else:
                enhanced_image_prompt = f"{style} educational diagram of {user_query}. Related concepts: {context_text}. Clean, labeled, high quality, professional."
            
            metadata = {
                "context_enhanced": len(retrieved_docs) > 0,
                "related_concepts": context_text,
                "style": style
            }
            
            logger.info(f"Enhanced image prompt for: {user_query}")
            return enhanced_image_prompt, metadata
            
        except Exception as e:
            logger.error(f"Error enhancing image prompt: {str(e)}")
            # Fallback
            fallback_prompt = f"{style} educational diagram of {image_prompt or user_query}, clean, labeled, high quality"
            return fallback_prompt, {"error": str(e), "context_enhanced": False}


def build_rag_prompt(
    user_query: str,
    topic: str,
    level: str = "basic",
    top_k: int = 3,
    use_context: bool = True
) -> Tuple[str, Dict]:
    """
    Convenience function to build a RAG-enhanced prompt.
    
    Args:
        user_query: User's question/topic
        topic: Educational topic
        level: Difficulty level
        top_k: Number of documents to retrieve
        use_context: Whether to use RAG context
    
    Returns:
        Tuple of (prompt, metadata)
    """
    if not use_context:
        pipeline = RAGPipeline(retrieval_top_k=0)
        return pipeline._build_basic_prompt(user_query, topic, level), {"rag_enabled": False}
    
    pipeline = RAGPipeline(retrieval_top_k=top_k)
    return pipeline.process_query(user_query, topic, level)


def build_enhanced_image_prompt(
    user_query: str,
    image_prompt: str = None,
    style: str = "diagram",
    top_k: int = 2
) -> Tuple[str, Dict]:
    """
    Convenience function to build an enhanced image prompt with RAG context.
    
    Args:
        user_query: User's query
        image_prompt: User-provided image prompt
        style: Image style
        top_k: Number of context documents
    
    Returns:
        Tuple of (enhanced_image_prompt, metadata)
    """
    pipeline = RAGPipeline(retrieval_top_k=top_k)
    return pipeline.process_image_generation_query(user_query, image_prompt or user_query, style)
