from __future__ import annotations

import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from src.core.config import settings

logger = logging.getLogger(__name__)

_embedding_model: HuggingFaceEmbeddings | None = None
_chroma_client: chromadb.PersistentClient | None = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"加载Embedding模型: {settings.embedding_model}")
        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model


def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def get_or_create_collection(space_id: int) -> chromadb.Collection:
    """每个知识空间对应ChromaDB中的一个独立集合"""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=f"space_{space_id}",
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks_to_vector_store(space_id: int, chunk_ids: list[int], contents: list[str]) -> None:
    """将文本片段向量化并存入ChromaDB"""
    model = get_embedding_model()
    collection = get_or_create_collection(space_id)

    embeddings = model.embed_documents(contents)
    collection.add(
        ids=[str(cid) for cid in chunk_ids],
        embeddings=embeddings,
        documents=contents,
    )
    logger.info(f"知识空间{space_id}: 已向量化并存储 {len(contents)} 个片段")


def search_similar_chunks(space_id: int, query: str, top_k: int = 4) -> list[dict]:
    """在知识空间中搜索与问题最相关的片段"""
    model = get_embedding_model()
    collection = get_or_create_collection(space_id)

    query_embedding = model.embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    if not results["ids"][0]:
        return []

    return [
        {"chunk_id": int(cid), "content": doc, "distance": dist}
        for cid, doc, dist in zip(
            results["ids"][0],
            results["documents"][0],
            results["distances"][0],
        )
    ]


def delete_space_from_vector_store(space_id: int) -> None:
    """删除知识空间时同步删除ChromaDB中的集合"""
    client = get_chroma_client()
    try:
        client.delete_collection(f"space_{space_id}")
        logger.info(f"已删除知识空间{space_id}的向量集合")
    except Exception:
        pass


def delete_chunks_from_vector_store(space_id: int, chunk_ids: list[int]) -> None:
    """删除文档时同步删除该文档的所有向量"""
    collection = get_or_create_collection(space_id)
    collection.delete(ids=[str(cid) for cid in chunk_ids])
