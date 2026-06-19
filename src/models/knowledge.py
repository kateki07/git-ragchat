import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base


class Collection(Base):
    __tablename__ = "collection"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    cmetadata = Column(JSON, nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

    files = relationship("File", back_populates="collection", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="collection")


class File(Base):
    __tablename__ = "file"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String(50), nullable=False)
    file_extension = Column(String(10), nullable=False)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collection.uuid", ondelete="CASCADE"), nullable=False)
    cmetadata = Column(JSON, nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

    collection = relationship("Collection", back_populates="files")
    chunks = relationship("Chunk", back_populates="file", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="file")


class Chunk(Base):
    __tablename__ = "chunk"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("file.uuid", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=True)
    context = Column(String, nullable=False)
    index = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False, default=0)  # 0=待处理 1=已向量化 2=失败
    create_time = Column(DateTime(timezone=True), server_default=func.now())

    file = relationship("File", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False)
