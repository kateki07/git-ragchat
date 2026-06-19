from fastapi import APIRouter
from src.handler.knowledge_handler import router as knowledge_router
from src.handler.chat_handler import router as chat_router

router = APIRouter(prefix="/api")
router.include_router(knowledge_router)
router.include_router(chat_router)

__all__ = ["router"]
