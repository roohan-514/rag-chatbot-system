from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from config import get_settings
from database import get_chroma_client, get_or_create_collection
from models.schemas import QueryResponse, SourceDocument

settings = get_settings()

_session_memory: dict = {}


def get_embedding_function():
    if settings.embedding_model.startswith("openai"):
        return OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model.replace("openai/", ""),
        )
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def get_chat_memory(session_id: str = "default"):
    if session_id not in _session_memory:
        _session_memory[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )
    return _session_memory[session_id]


def query_documents(
    query: str,
    k: int = 4,
    session_id: str = "default",
) -> QueryResponse:
    embeddings = get_embedding_function()
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    sources = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            score = round(1.0 - float(dist), 4)
            sources.append(SourceDocument(
                content=doc[:200] + "..." if len(doc) > 200 else doc,
                filename=meta.get("filename", "unknown"),
                page=meta.get("page"),
                score=score,
            ))

    if settings.openai_api_key:
        llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.3,
        )
        memory = get_chat_memory(session_id)

        retriever = _ChromaRetriever(collection, embeddings, k)
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            verbose=False,
        )
        result = qa_chain.invoke({"question": query})
        answer = result["answer"]
    else:
        context = "\n\n".join(
            [s.content for s in sources]
        )
        answer = (
            f"Based on the retrieved documents:\n\n{context}\n\n"
            f"(OpenAI API key not configured — showing raw retrieval results. "
            f"Set OPENAI_API_KEY in .env for LLM-generated answers.)"
        )

    return QueryResponse(answer=answer, sources=sources)


class _ChromaRetriever:
    def __init__(self, collection, embeddings, k: int = 4):
        self.collection = collection
        self.embeddings = embeddings
        self.k = k

    def get_relevant_documents(self, query: str):
        results = self.collection.query(
            query_texts=[query],
            n_results=self.k,
            include=["documents", "metadatas"],
        )
        from langchain.schema import Document
        docs = []
        if results["documents"] and results["documents"][0]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                docs.append(Document(page_content=doc, metadata=meta))
        return docs

    async def aget_relevant_documents(self, query: str):
        return self.get_relevant_documents(query)
