from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ChunkEmbeddingDto(BaseModel):
    """チャンクとエンベディングの結合DTO（検索結果用）"""

    uuid: UUID
    file_id: UUID
    file_name: Optional[str] = None
    context: str
    index: int
    status: int
    collection_id: Optional[UUID] = None
    create_time: datetime

    model_config = {"from_attributes": True}
