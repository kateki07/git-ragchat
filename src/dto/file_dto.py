from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class FileDto(BaseModel):
    """ファイルDTO"""

    uuid: UUID
    file_name: str
    file_extension: str
    collection_id: UUID
    cmetadata: Optional[dict] = None
    create_time: datetime

    model_config = {"from_attributes": True}
