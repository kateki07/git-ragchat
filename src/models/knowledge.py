from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class KnowledgeSpace(Base):
    """知识空间：一个知识空间对应一个独立的知识库（类似文件夹）"""
    __tablename__ = "knowledge_spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    documents = relationship(
        "Document", back_populates="knowledge_space", cascade="all, delete-orphan"
    )
    conversations = relationship("Conversation", back_populates="knowledge_space")


class Document(Base):
    """上传的文档：一个文档属于一个知识空间"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_space_id = Column(
        Integer, ForeignKey("knowledge_spaces.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    # pending / processing / done / failed
    status = Column(String(20), nullable=False, default="pending")
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    knowledge_space = relationship("KnowledgeSpace", back_populates="documents")
    chunks = relationship(
        "Chunk", back_populates="document", cascade="all, delete-orphan"
    )


class Chunk(Base):
    """文档片段：文档被分割成的小块，每块单独向量化存储"""
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    knowledge_space_id = Column(
        Integer, ForeignKey("knowledge_spaces.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="chunks")
