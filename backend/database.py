import chromadb
from chromadb.config import Settings as ChromaSettings
from config import get_settings

settings = get_settings()


def get_chroma_client():
    return chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_or_create_collection(client=None):
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def get_collection_size() -> int:
    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        return collection.count()
    except Exception:
        return 0
