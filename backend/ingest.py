import os
import uuid
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from config import get_settings
from database import get_chroma_client, get_or_create_collection

settings = get_settings()


def get_embedding_function():
    if settings.embedding_model.startswith("openai"):
        return OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model.replace("openai/", ""),
        )
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def load_document(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".md":
        loader = UnstructuredMarkdownLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader.load()


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_documents(documents)


def generate_embeddings_and_store(chunks: List, filename: str) -> int:
    embeddings = get_embedding_function()
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    ids = []
    documents = []
    metadatas = []
    for i, chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        ids.append(chunk_id)
        documents.append(chunk.page_content)
        metadatas.append({
            "filename": filename,
            "chunk_index": i,
            "source": chunk.metadata.get("source", filename),
            "page": chunk.metadata.get("page", None),
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )
    return len(chunks)


def ingest_file(file_path: str) -> int:
    docs = load_document(file_path)
    chunks = split_documents(docs)
    filename = os.path.basename(file_path)
    chunk_count = generate_embeddings_and_store(chunks, filename)
    return chunk_count
