from fastapi import APIRouter
from src.api.v1 import chat_router, knowledge_router

router = APIRouter(prefix="/api")

router.include_router(chat_router)
router.include_router(knowledge_router)
