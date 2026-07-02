import os
import uuid
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models.schemas import (
    QueryRequest,
    QueryResponse,
    IngestResponse,
    DocumentInfo,
    HealthResponse,
)
from database import get_collection_size
from ingest import ingest_file
from query import query_documents

settings = get_settings()

app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation Chatbot - Ingestion & Query",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ingested_files: dict = {}


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        collection_size=get_collection_size(),
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".txt", ".md"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: .pdf, .txt, .md",
        )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    try:
        content = await file.read()
        tmp.write(content)
        tmp.close()

        chunk_count = ingest_file(tmp.name)
        ingested_files[file.filename] = chunk_count
        return IngestResponse(
            message=f"Successfully ingested '{file.filename}'",
            filename=file.filename,
            chunk_count=chunk_count,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        return query_documents(query=request.query, k=request.k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=list[DocumentInfo])
async def list_documents():
    docs = []
    for filename, chunk_count in ingested_files.items():
        docs.append(DocumentInfo(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, filename)),
            filename=filename,
            chunk_count=chunk_count,
            content_preview=f"{chunk_count} chunks ingested",
        ))
    return docs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
