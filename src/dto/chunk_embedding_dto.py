from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ChunkEmbeddingDto(BaseModel):
    """ベクトル化処理用チャンクDTO"""

    chunk_id: UUID
    file_id: UUID
    file_name: Optional[str] = None
    context: str
    collection_id: Optional[UUID] = None

    model_config = {"from_attributes": True}
