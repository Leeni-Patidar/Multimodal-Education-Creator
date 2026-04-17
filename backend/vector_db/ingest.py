"""
Data ingestion for ChromaDB.
Handles loading educational content into the vector database.
"""

import logging
from uuid import uuid4
from vector_db.db import get_vector_db

logger = logging.getLogger(__name__)


# Sample educational content database
SAMPLE_CONTENT = [
    {
        "title": "Machine Learning Fundamentals",
        "content": """Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. 
        It works by identifying patterns in training data and using them to make predictions on new data. 
        Key concepts include: supervised learning (with labeled data), unsupervised learning (finding patterns), and reinforcement learning (learning from rewards).
        Applications include image recognition, natural language processing, recommendation systems, and predictive analytics.""",
        "category": "AI/ML",
        "level": "intermediate"
    },
    {
        "title": "Deep Learning and Neural Networks",
        "content": """Deep learning uses artificial neural networks with multiple layers (hence 'deep') to learn complex patterns.
        Each neuron performs a weighted sum followed by an activation function. Backpropagation trains networks by computing gradients.
        Common architectures: CNNs for images, RNNs for sequences, Transformers for NLP.
        Deep learning powers modern AI applications like ChatGPT, image generation, and autonomous driving.""",
        "category": "AI/ML",
        "level": "advanced"
    },
    {
        "title": "Python Programming Basics",
        "content": """Python is a high-level programming language known for readability and versatility.
        Data types include: integers, floats, strings, lists, dictionaries, sets, and tuples.
        Control structures: if-else, for loops, while loops, and functions enable code organization.
        Libraries like NumPy, Pandas, and Matplotlib make Python powerful for data science and scientific computing.
        Python is widely used in web development, automation, AI/ML, and data analysis.""",
        "category": "Programming",
        "level": "beginner"
    },
    {
        "title": "Data Structures and Algorithms",
        "content": """Data structures organize data efficiently for processing. Common structures: arrays, linked lists, stacks, queues, trees, and graphs.
        Algorithms solve problems step-by-step. Key algorithm types: sorting (quicksort, mergesort), searching (binary search), graph traversal (DFS, BFS).
        Time complexity measures algorithm efficiency: O(1) constant, O(log n) logarithmic, O(n) linear, O(n²) quadratic.
        Space complexity measures memory usage. Choosing the right data structure and algorithm is crucial for performance.""",
        "category": "Computer Science",
        "level": "intermediate"
    },
    {
        "title": "Web Development with FastAPI",
        "content": """FastAPI is a modern web framework for building APIs with Python. It's built on Starlette and Pydantic.
        Key features: automatic API documentation, type hints, async/await support, and high performance.
        RESTful APIs use HTTP methods: GET (retrieve), POST (create), PUT (update), DELETE (remove).
        FastAPI handles request validation, serialization, and CORS middleware for cross-origin requests.
        It's production-ready and suitable for microservices, backend APIs, and real-time applications.""",
        "category": "Web Development",
        "level": "intermediate"
    },
    {
        "title": "Database Design and SQL",
        "content": """Relational databases organize data in tables with rows and columns.
        SQL (Structured Query Language) operations: SELECT (query), INSERT (add), UPDATE (modify), DELETE (remove).
        Key concepts: primary keys (unique identifiers), foreign keys (relationships), normalization (eliminating redundancy).
        ACID properties ensure data reliability: Atomicity, Consistency, Isolation, Durability.
        Popular databases: PostgreSQL, MySQL, SQL Server. NoSQL alternatives: MongoDB, Cassandra for unstructured data.""",
        "category": "Database",
        "level": "intermediate"
    },
    {
        "title": "Vectors and Embeddings",
        "content": """Vectors represent data as numerical lists, enabling mathematical operations and similarity calculations.
        Embeddings map text/images to high-dimensional vectors where similar items are close together.
        Word embeddings: Word2Vec, GloVe represent words in meaningful space capturing semantic relationships.
        Sentence embeddings: tools like sentence-transformers create fixed-size vectors for entire sentences.
        Vector databases (ChromaDB, Pinecone, Weaviate) store embeddings for fast similarity search via cosine distance or Euclidean distance.""",
        "category": "AI/ML",
        "level": "advanced"
    },
    {
        "title": "Retrieval-Augmented Generation (RAG)",
        "content": """RAG combines retrieval and generation to enhance LLM outputs with relevant context.
        Process: 1) Embed user query, 2) Retrieve similar documents from vector DB, 3) Create prompt with context, 4) Generate response with LLM.
        Benefits: more accurate answers, reduced hallucinations, ability to reference specific documents, knowledge cutoff mitigation.
        Applications: question-answering systems, chatbots with document access, customer support automation.
        Key components: embeddings model, vector database, retrieval ranking, prompt engineering.""",
        "category": "AI/ML",
        "level": "advanced"
    },
    {
        "title": "Image Generation and Diffusion Models",
        "content": """Image generation models create images from text descriptions.
        Diffusion models: start with noise and iteratively denoise to generate images matching the description.
        Popular models: DALL-E (by OpenAI), Stable Diffusion (open-source), FLUX by Black Forest Labs.
        Techniques: text conditioning embeds descriptions, attention mechanisms align text and visual features.
        Applications: art generation, UI/UX prototyping, educational diagrams, content creation, data augmentation.""",
        "category": "AI/ML",
        "level": "advanced"
    },
    {
        "title": "API Design Principles",
        "content": """Well-designed APIs are intuitive, scalable, and maintainable.
        RESTful principles: resources as nouns, HTTP verbs as actions, stateless design, standard status codes.
        Best practices: versioning (v1, v2), consistent naming, pagination, filtering, sorting, error handling.
        Authentication: API keys, JWT tokens, OAuth 2.0 for secure access.
        Documentation: OpenAPI/Swagger specs, clear examples, response schemas enable developer experience.
        Rate limiting protects services; caching improves performance; monitoring tracks API health.""",
        "category": "Web Development",
        "level": "intermediate"
    },
]


def ingest_sample_content():
    """
    Ingest sample educational content into ChromaDB.
    This function can be called during startup or via a management endpoint.
    """
    try:
        db = get_vector_db()
        collection = db.collection
        
        # Check if content already exists
        count = collection.count()
        if count > 0:
            logger.info(f"Collection already contains {count} documents. Skipping ingestion.")
            return count
        
        logger.info(f"Ingesting {len(SAMPLE_CONTENT)} documents into ChromaDB...")
        
        documents = []
        metadatas = []
        ids = []
        
        for item in SAMPLE_CONTENT:
            doc_id = str(uuid4())
            documents.append(item["content"])
            metadatas.append({
                "title": item["title"],
                "category": item["category"],
                "level": item["level"]
            })
            ids.append(doc_id)
        
        # Add documents to collection (ChromaDB handles embedding)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully ingested {len(SAMPLE_CONTENT)} documents")
        return len(SAMPLE_CONTENT)
        
    except Exception as e:
        logger.error(f"Error ingesting content: {str(e)}")
        raise


def add_custom_content(title: str, content: str, category: str = "General", level: str = "beginner") -> str:
    """
    Add custom educational content to the vector database.
    
    Args:
        title: Content title
        content: Content text
        category: Content category
        level: Difficulty level (beginner, intermediate, advanced)
    
    Returns:
        Document ID
    """
    try:
        db = get_vector_db()
        collection = db.collection
        
        doc_id = str(uuid4())
        
        collection.add(
            documents=[content],
            metadatas=[{
                "title": title,
                "category": category,
                "level": level
            }],
            ids=[doc_id]
        )
        
        logger.info(f"Added custom content with ID: {doc_id}, Title: {title}")
        return doc_id
        
    except Exception as e:
        logger.error(f"Error adding custom content: {str(e)}")
        raise


def get_collection_info() -> dict:
    """Get information about the ChromaDB collection."""
    try:
        db = get_vector_db()
        stats = db.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        return {"error": str(e)}
