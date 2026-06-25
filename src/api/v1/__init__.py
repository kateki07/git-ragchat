from src.api.v1.chat import router as chat_router
from src.api.v1.user import router as user_router
from src.api.v1.collections import router as collections_router
from src.api.v1.files import router as files_router
from src.api.v1.chunks import router as chunks_router
from src.api.v1.dicts import router as dicts_router

__all__ = [
    "chat_router",
    "user_router",
    "collections_router",
    "files_router",
    "chunks_router",
    "dicts_router",
]
