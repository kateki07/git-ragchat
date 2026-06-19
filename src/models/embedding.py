import uuid
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from src.models.base import Base

EMBEDDING_DIM = 512  # BAAI/bge-small-zh-v1.5 的向量维度


class Embedding(Base):
    __tablename__ = "embedding"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunk.uuid", ondelete="CASCADE"), nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey("file.uuid", ondelete="CASCADE"), nullable=False)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collection.uuid", ondelete="CASCADE"), nullable=False)
    embedding_vector = Column(Vector(EMBEDDING_DIM), nullable=True)
    search_vector = Column(TSVECTOR, nullable=True)
    cmetadata = Column(JSON, nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

    chunk = relationship("Chunk", back_populates="embedding")
    file = relationship("File", back_populates="embeddings")
    collection = relationship("Collection", back_populates="embeddings")
