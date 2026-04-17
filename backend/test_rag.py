#!/usr/bin/env python
"""
Test script for RAG pipeline.
Demonstrates RAG functionality with example queries.

Usage:
    python test_rag.py              # Run default tests
    python test_rag.py --query "your question"  # Test custom query
"""

import sys
import os
import logging
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from vector_db.db import get_vector_db
from vector_db.ingest import ingest_sample_content
from vector_db.retriever import DocumentRetriever, quick_retrieve_formatted
from rag.pipeline import build_rag_prompt, build_enhanced_image_prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Test queries
TEST_QUERIES = [
    {
        "query": "What is machine learning and how does it work?",
        "topic": "Machine Learning",
        "level": "intermediate"
    },
    {
        "query": "Explain neural networks and deep learning",
        "topic": "Deep Learning",
        "level": "advanced"
    },
    {
        "query": "How does RAG improve LLM responses?",
        "topic": "RAG",
        "level": "advanced"
    },
    {
        "query": "Tell me about Python programming basics",
        "topic": "Python",
        "level": "beginner"
    },
]


def test_retrieval():
    """Test document retrieval functionality."""
    print("\n" + "=" * 70)
    print("TEST 1: Document Retrieval")
    print("=" * 70)
    
    retriever = DocumentRetriever(top_k=3)
    
    test_query = "What are machine learning and its applications?"
    
    print(f"\nQuery: {test_query}\n")
    print("Retrieved Documents:")
    print("-" * 70)
    
    docs = retriever.retrieve(test_query)
    for i, doc in enumerate(docs, 1):
        print(f"\n[{i}] {doc['title']}")
        print(f"    Category: {doc['category']} | Level: {doc['level']}")
        print(f"    Similarity Score: {doc['similarity_score']:.1%}")
        print(f"    Content: {doc['content'][:150]}...")
    
    return len(docs) > 0


def test_formatted_retrieval():
    """Test formatted retrieval output."""
    print("\n" + "=" * 70)
    print("TEST 2: Formatted Context Retrieval")
    print("=" * 70)
    
    query = "Tell me about embeddings and vectors"
    print(f"\nQuery: {query}\n")
    
    formatted_context = quick_retrieve_formatted(query, top_k=2)
    print("Formatted Context:")
    print("-" * 70)
    print(formatted_context)
    
    return "Retrieved Context" in formatted_context


def test_rag_pipeline():
    """Test RAG pipeline with various queries."""
    print("\n" + "=" * 70)
    print("TEST 3: RAG Pipeline Enhancement")
    print("=" * 70)
    
    all_passed = True
    for idx, test_case in enumerate(TEST_QUERIES[:2], 1):  # Test first 2 queries
        print(f"\n[Test 3.{idx}] Query: {test_case['query']}")
        print("-" * 70)
        
        try:
            # Build RAG prompt
            prompt, metadata = build_rag_prompt(
                user_query=test_case['query'],
                topic=test_case['topic'],
                level=test_case['level'],
                top_k=2
            )
            
            print(f"RAG Enabled: {metadata.get('rag_enabled', False)}")
            print(f"Retrieved Documents: {metadata.get('retrieved_docs_count', 0)}")
            
            if metadata.get('rag_enabled'):
                print(f"Document Titles: {', '.join(metadata.get('retrieved_titles', []))}")
                print(f"Avg Similarity: {metadata.get('avg_similarity_score', 0):.1%}")
            
            print(f"\nGenerated Prompt (first 300 chars):")
            print(prompt[:300] + "...")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            all_passed = False
    
    return all_passed


def test_image_prompt_enhancement():
    """Test image prompt enhancement with RAG."""
    print("\n" + "=" * 70)
    print("TEST 4: Image Prompt Enhancement")
    print("=" * 70)
    
    queries = [
        ("Neural networks", "diagram"),
        ("Python data structures", "infographic"),
    ]
    
    for query, style in queries:
        print(f"\nQuery: {query} (Style: {style})")
        print("-" * 70)
        
        try:
            enhanced_prompt, metadata = build_enhanced_image_prompt(
                user_query=query,
                image_prompt=None,
                style=style,
                top_k=2
            )
            
            print(f"Context Enhanced: {metadata.get('context_enhanced', False)}")
            print(f"Related Concepts: {metadata.get('related_concepts', 'N/A')}")
            print(f"\nEnhanced Image Prompt:\n{enhanced_prompt}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("RAG PIPELINE TEST SUITE")
    print("=" * 70)
    
    try:
        # Initialize vector DB
        print("\nInitializing Vector Database...")
        db = get_vector_db()
        db.initialize()
        
        # Ingest sample content if not already done
        collection_count = db.get_collection_stats().get('count', 0)
        if collection_count == 0:
            print("Ingesting sample content...")
            ingest_sample_content()
        else:
            print(f"Collection already contains {collection_count} documents")
        
        # Run tests
        results = {
            "Retrieval Test": test_retrieval(),
            "Formatted Retrieval": test_formatted_retrieval(),
            "RAG Pipeline": test_rag_pipeline(),
            "Image Prompt Enhancement": test_image_prompt_enhancement(),
        }
        
        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        for test_name, passed in results.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{test_name}: {status}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n✓ All tests passed!")
            print("=" * 70)
            return 0
        else:
            print("\n✗ Some tests failed")
            print("=" * 70)
            return 1
        
    except Exception as e:
        logger.error(f"Fatal error during testing: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
