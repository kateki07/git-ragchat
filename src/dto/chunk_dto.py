from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ChunkDto(BaseModel):
    """チャンクDTO"""

    uuid: UUID
    file_id: UUID
    file_name: Optional[str] = None
    context: str
    index: int
    status: int
    create_time: datetime

    model_config = {"from_attributes": True}
