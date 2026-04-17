#!/usr/bin/env python
"""
Data ingestion script for ChromaDB.
Run this script to initialize and populate the vector database with sample content.

Usage:
    python ingest_data.py            # Ingest sample content
    python ingest_data.py --reset    # Reset and re-ingest
    python ingest_data.py --stats    # Show database statistics
"""

import sys
import os
import logging
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from vector_db.db import get_vector_db
from vector_db.ingest import ingest_sample_content, get_collection_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def main():
    """Main ingestion function."""
    
    # Parse command line arguments
    reset = "--reset" in sys.argv
    show_stats = "--stats" in sys.argv
    
    logger.info("=" * 60)
    logger.info("ChromaDB Data Ingestion Script")
    logger.info("=" * 60)
    
    try:
        # Step 1: Initialize vector DB
        logger.info("\n1. Initializing Vector Database...")
        db = get_vector_db()
        db.initialize()
        logger.info("✓ Vector DB initialized")
        
        # Step 2: Reset if requested
        if reset:
            logger.info("\n2. Resetting collection...")
            db.reset_collection()
            logger.info("✓ Collection reset")
        
        # Step 3: Ingest content
        logger.info("\n3. Ingesting sample educational content...")
        count = ingest_sample_content()
        logger.info(f"✓ Successfully ingested {count} documents")
        
        # Step 4: Show statistics
        logger.info("\n4. Collection Statistics:")
        info = get_collection_info()
        logger.info(f"   Total documents: {info.get('count', 0)}")
        logger.info(f"   Collection name: {info.get('name', 'N/A')}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Ingestion completed successfully!")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n✗ Error during ingestion: {str(e)}")
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
