import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CollectionCreate(BaseModel):
    name: str
    cmetadata: Optional[dict] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    cmetadata: Optional[dict] = None


class CollectionOut(BaseModel):
    uuid: uuid.UUID
    name: str
    cmetadata: Optional[dict]
    create_time: datetime

    model_config = {"from_attributes": True}


class FileOut(BaseModel):
    uuid: uuid.UUID
    file_name: str
    file_extension: str
    collection_id: uuid.UUID
    create_time: datetime

    model_config = {"from_attributes": True}


class ChunkOut(BaseModel):
    uuid: uuid.UUID
    file_id: uuid.UUID
    context: str
    index: int
    status: int

    model_config = {"from_attributes": True}
