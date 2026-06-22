from typing import Optional
from pydantic import BaseModel


class AiExtMessageDto(BaseModel):
    """AI外部メッセージDTO"""

    id: int
    run_id: Optional[str] = None
    ext_context: Optional[str] = None

    model_config = {"from_attributes": True}
