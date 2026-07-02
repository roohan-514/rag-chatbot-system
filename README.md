# RAG Chatbot System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)
[![LangChain](https://img.shields.io/badge/LangChain-0.1-orange.svg)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4-yellow.svg)](https://chromadb.com)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

A production-quality Retrieval-Augmented Generation (RAG) chatbot that answers questions based on your documents. Built with **LangChain**, **ChromaDB**, **FastAPI**, and **React**.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   FastAPI   │────▶│  LangChain      │────▶│  ChromaDB    │
│  (Backend)  │     │  (Orchestration) │     │  (Vector DB) │
└─────────────┘     └─────────────────┘     └──────────────┘
    │                                               │
    ▼                                               ▼
┌─────────────┐                          ┌──────────────────┐
│  React App  │                          │  Embedding Model │
│  (Frontend) │                          │ (OpenAI/ST)      │
└─────────────┘                          └──────────────────┘
```

### How RAG Works

1. **Ingest** — Documents (PDF, TXT, MD) are loaded and split into chunks.
2. **Embed** — Each chunk is converted into a vector embedding using Sentence-Transformers or OpenAI embeddings.
3. **Store** — Embeddings are stored in ChromaDB (vector database) for efficient similarity search.
4. **Retrieve** — When a query arrives, it's embedded and ChromaDB returns the most similar chunks.
5. **Generate** — Retrieved chunks are passed as context to an LLM (OpenAI GPT) which generates a grounded answer with source citations.

---

## Tech Stack

| Component  | Technology                                      |
| ---------- | ----------------------------------------------- |
| Backend    | Python, FastAPI, Uvicorn                        |
| Framework  | LangChain                                       |
| Vector DB  | ChromaDB                                        |
| Embeddings | Sentence-Transformers / OpenAI Embeddings       |
| LLM        | OpenAI GPT-3.5-Turbo / GPT-4                    |
| Frontend   | React 18, Vite, Axios                           |
| Container  | Docker & Docker Compose                         |

---

## Features

- 📄 **Multi-format document ingestion** — PDF, TXT, Markdown
- ✂️ **Smart chunking** with RecursiveCharacterTextSplitter
- 🔍 **Semantic search** using cosine similarity on vector embeddings
- 🤖 **LLM-powered answers** with source citations
- 🗂️ **Conversation memory** for multi-turn dialogues
- 🎨 **Dark/Light mode** UI
- 📤 **Drag-and-drop file upload**
- 📋 **Source document panel** with relevance scores
- 🐳 **Docker support** for easy deployment

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional)
- OpenAI API key (optional — falls back to raw retrieval without it)

---

## Installation

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

Copy the environment file and configure it:

```bash
cp .env.example .env
# Edit .env — set your OPENAI_API_KEY
```

Run the backend:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Environment Variables

| Variable           | Default                                    | Description                    |
| ------------------ | ------------------------------------------ | ------------------------------ |
| `OPENAI_API_KEY`   | —                                          | OpenAI API key                 |
| `OPENAI_MODEL`     | `gpt-3.5-turbo`                            | OpenAI model name              |
| `EMBEDDING_MODEL`  | `sentence-transformers/all-MiniLM-L6-v2`   | Embedding model                |
| `CHROMA_PERSIST_DIR` | `./chroma_db`                            | ChromaDB persist directory     |
| `CHUNK_SIZE`       | `1000`                                     | Text chunk size                |
| `CHUNK_OVERLAP`    | `200`                                      | Chunk overlap                  |
| `COLLECTION_NAME`  | `rag_documents`                            | ChromaDB collection name       |
| `HOST`             | `0.0.0.0`                                  | Server host                    |
| `PORT`             | `8000`                                     | Server port                    |

---

## Usage

### Ingesting Documents

You can upload documents through:
- **Frontend UI** — Drag & drop files in the sidebar
- **API** — `POST /ingest` with a multipart file upload
- **cURL**:
  ```bash
  curl -X POST http://localhost:8000/ingest \
    -F "file=@sample_docs/sample.txt"
  ```

### Asking Questions

- **Frontend UI** — Type your question in the chat input
- **API**:
  ```bash
  curl -X POST http://localhost:8000/query \
    -H "Content-Type: application/json" \
    -d '{"query": "What is RAG?", "k": 4}'
  ```
- **API**:
  ```json
  {
    "answer": "RAG stands for Retrieval-Augmented Generation...",
    "sources": [
      {
        "content": "Retrieval-Augmented Generation is...",
        "filename": "sample.txt",
        "page": null,
        "score": 0.92
      }
    ]
  }
  ```

---

## API Documentation

| Method | Endpoint       | Description                          |
| ------ | -------------- | ------------------------------------ |
| GET    | `/health`      | Health check + collection size       |
| POST   | `/ingest`      | Upload and ingest a document         |
| POST   | `/query`       | Ask a question                       |
| GET    | `/documents`   | List ingested documents              |

Full interactive API docs at `http://localhost:8000/docs` (Swagger UI).

---

## Docker Setup

```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up -d
```

Create a `backend/.env` file before running (copy from `.env.example`).

---

## Sample Queries

After ingesting `sample_docs/sample.txt`:

| Query                                          | Expected Result                              |
| ---------------------------------------------- | -------------------------------------------- |
| "What is RAG?"                                 | Defines Retrieval-Augmented Generation       |
| "What are the advantages of RAG?"              | Lists 3 key advantages                       |
| "What file formats are supported?"             | PDF, TXT, Markdown                           |
| "How does the ingestion pipeline work?"        | Describes load → split → embed → store       |

---

## Project Structure

```
rag-chatbot-system/
├── README.md
├── .gitignore
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Configuration via pydantic-settings
│   ├── ingest.py              # Document ingestion pipeline
│   ├── query.py               # Query processing + retrieval
│   ├── database.py            # ChromaDB client setup
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # Pydantic models
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   └── SourcePanel.jsx
│   │   └── services/
│   │       └── api.js
│   └── public/
└── sample_docs/
    └── sample.txt
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request.

Please ensure your code passes linting and basic sanity checks before submitting.

---

## License

MIT
