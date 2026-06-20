from pydantic import BaseModel


class UserDto(BaseModel):
    """ユーザーデータ転送オブジェクト"""

    id: str
    name: str

    model_config = {
        'from_attributes': True
    }
