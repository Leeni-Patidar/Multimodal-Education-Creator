# Multimodal Education Creator

An intelligent AI-powered platform that generates personalized educational content combining text explanations with visual aids. The system uses Retrieval-Augmented Generation (RAG) to provide context-aware learning materials tailored to different proficiency levels.

## 🎯 Key Features

- **Multi-level Content Generation**: Create educational materials at Basic, Intermediate, and Advanced levels
- **RAG-Powered Learning**: Retrieval-Augmented Generation for context-aware, knowledge-rich responses
- **Image Generation**: Auto-generate thematic visual explanations using FLUX.1 image model
- **Flashcard Creation**: Automatic generation of study flashcards from educational content
- **Content History**: Track and reload previously generated educational materials
- **Real-time Processing**: Fast API backend with optimized performance
- **Vector Database**: ChromaDB integration for efficient document retrieval and semantic search

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **LLM Integration**: Groq API for text generation
- **Image Generation**: Hugging Face Inference API (FLUX.1-schnell model)
- **Vector Database**: ChromaDB with Sentence Transformers embeddings
- **Server**: Uvicorn
- **Dependencies**: Pydantic, Pillow, NumPy

### Frontend
- **Framework**: React 19 with Vite
- **Styling**: Tailwind CSS with PostCSS
- **HTTP Client**: Axios
- **UI Components**: Custom React components for form, output, history, and flashcards


## 🚀 Getting Started

### Prerequisites

- Python 3.8+ (for backend)
- Node.js 16+ and npm (for frontend)
- API Keys:
  - **GROQ_API_KEY**: Get from [Groq Console](https://console.groq.com)
  - **HF_API_KEY**: Get from [Hugging Face](https://huggingface.co/settings/tokens)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_api_key_here
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
RAG_ENABLED=true
```



### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (if needed for environment-specific API endpoints):
```env
VITE_API_BASE_URL=http://localhost:8000
```

## ▶️ Running the Application

### Option 1: Run Backend and Frontend Separately

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```
Backend runs on: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`



### Frontend
```bash
npm run dev      # Start development server with HMR
npm run build    # Build for production
npm run lint     # Run ESLint
npm run preview  # Preview production build
```

### Backend
```bash
uvicorn main:app --reload    # Start with auto-reload
python ingest_data.py         # Ingest documents for RAG
```

## 🔧 Environment Variables

### Backend (.env)
- `GROQ_API_KEY` - Required: Groq API key for LLM
- `HF_API_KEY` - Required: Hugging Face API key for images
- `HF_IMAGE_MODEL` - Image model to use (default: black-forest-labs/FLUX.1-schnell)
- `RAG_ENABLED` - Enable/disable RAG pipeline (default: true)

### Frontend (.env)
- `VITE_API_BASE_URL` - Backend API base URL (default: http://localhost:8000)





