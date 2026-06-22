from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CollectionDto(BaseModel):
    """コレクションDTO"""

    uuid: UUID
    name: str
    cmetadata: Optional[dict] = None
    create_time: datetime

    model_config = {"from_attributes": True}
