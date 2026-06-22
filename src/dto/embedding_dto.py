from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Json
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR


class EmbeddingDto(BaseModel):
    """エンベディングDTO"""

    uuid: UUID
    file_id: Optional[UUID] = None
    chunk_id: Optional[UUID] = None
    collection_id: Optional[UUID] = None
    embedding_vector: Optional[Vector] = None
    search_vector: Optional[TSVECTOR] = None
    cmetadata: Optional[Json] = None
    create_time: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
    }
