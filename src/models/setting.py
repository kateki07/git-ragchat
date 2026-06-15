from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from src.core.database import Base


class SystemSetting(Base):
    """系统动态配置：存储可在运行时修改的配置项，如LLM模型、提示词模板等"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
