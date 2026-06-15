from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class KnowledgeSpaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class KnowledgeSpaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class KnowledgeSpaceOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: int
    knowledge_space_id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChunkOut(BaseModel):
    id: int
    document_id: int
    content: str
    chunk_index: int

    model_config = {"from_attributes": True}
