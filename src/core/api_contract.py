from typing import Any, Optional
from pydantic import BaseModel
from src.core.response_code import ResponseCode


class APIContract(BaseModel):
    """統一APIレスポンス形式"""

    code: int
    message: str
    data: Optional[Any] = None

    @classmethod
    def success(cls, data: Any = None) -> "APIContract":
        """正常レスポンス"""
        return cls(code=ResponseCode.SUCCESS.code, message=ResponseCode.SUCCESS.message, data=data)

    @classmethod
    def error(cls, message: str = None, code: int = None) -> "APIContract":
        """エラーレスポンス"""
        return cls(
            code=code or ResponseCode.INTERNAL_ERROR.code,
            message=message or ResponseCode.INTERNAL_ERROR.message,
            data=None,
        )

    @classmethod
    def not_found(cls, message: str = None) -> "APIContract":
        """リソース未存在レスポンス"""
        return cls(
            code=ResponseCode.NOT_FOUND.code,
            message=message or ResponseCode.NOT_FOUND.message,
            data=None,
        )
