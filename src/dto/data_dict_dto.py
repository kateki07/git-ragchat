from typing import Optional
from pydantic import BaseModel


class DataDictDto(BaseModel):
    """データ辞書DTO"""

    id: int
    key: str
    value: Optional[str] = None

    model_config = {"from_attributes": True}
