from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.api_contract import APIContract
from src.db.pg_db import get_db
from src.handler.chat_model_handler import ChatModelHandler
from src.services.user_servcie import UserService
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["chat"], prefix="/chat")


class ChatRequest(BaseModel):
    user_id: str
    message: str
    collection_id: str


@router.post("/")
async def chat_with_user(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """ユーザーとのチャットを処理するエンドポイント"""
    logger.info(
        f"用户ID: {req.user_id}, collection_id:{req.collection_id}, 消息: {req.message}"
    )

    user_service = UserService(db)
    user = await user_service.get_by_id(req.user_id)
    if not user:
        return APIContract.error("User not found")
    logger.info(f"用户信息: {user}")

    chat_model_handler = ChatModelHandler()

    if not req.collection_id:
        logger.info("collection_id is None, 走通用模式")
        response = await chat_model_handler.get_llm_response(req.user_id, req.message)
    else:
        logger.info("collection_id is not None, 走RAG模式")
        response = None  # RAGモードは後で実装

    if not response:
        return APIContract.error("AI大模型会話失敗")

    logger.info(f"AI回复: {response}")
    return APIContract.success(response)
