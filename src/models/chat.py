from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class Conversation(Base):
    """会话：一次对话记录。knowledge_space_id为空=普通对话，有值=RAG对话"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), default="新会话")
    knowledge_space_id = Column(
        Integer, ForeignKey("knowledge_spaces.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    knowledge_space = relationship("KnowledgeSpace", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    """消息：会话中的单条消息，role为user或assistant"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(20), nullable=False)   # user / assistant
    content = Column(Text, nullable=False)
    # RAG模式下，记录引用的chunk id列表，用于前端显示引用来源
    source_chunks = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
