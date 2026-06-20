from enum import Enum


class ResponseCode(Enum):
    """APIレスポンスコード定義"""

    SUCCESS = (200, "成功")
    BAD_REQUEST = (400, "リクエストが不正です")
    UNAUTHORIZED = (401, "認証が必要です")
    FORBIDDEN = (403, "アクセス権限がありません")
    NOT_FOUND = (404, "リソースが見つかりません")
    INTERNAL_ERROR = (500, "サーバー内部エラー")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
