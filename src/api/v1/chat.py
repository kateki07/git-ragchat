from fastapi import APIRouter

router = APIRouter(tags=["chat"], prefix="/chat")


@router.get("/")
def get_chat():
    """チャットエンドポイント（実装予定）"""
    return {"message": "This is a chat endpoint"}
