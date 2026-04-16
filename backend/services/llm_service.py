import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Create session with connection pooling and retries
_session = None

def get_session():
    global _session
    if _session is None:
        _session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        _session.mount("https://", adapter)
    return _session

def generate_text(prompt):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in environment variables")
    
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Use fastest available model: llama-3.1-8b-instant is optimized for low-latency
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        logger.info(f"Calling Groq API with faster model...")
        session = get_session()
        response = session.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Groq API error: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            response.raise_for_status()
            
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Groq API request error: {str(e)}")
        raise