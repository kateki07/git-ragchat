import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import router
from src.db.pg_db import init_db
from src.core.logging_config import setup_logging
from src.core.embedding_manager import initialize_embeddings
from src.job.scheduler_setup import scheduled_job
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    await init_db()

    try:
        await initialize_embeddings()
        logger.info("埋め込みモデル初期化成功")
    except Exception as e:
        logger.error(f"埋め込みモデル初期化失敗: {e}")
        raise

    task = asyncio.create_task(scheduled_job())
    logger.info("定期ジョブ起動成功")

    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("定期ジョブ停止完了")


app = FastAPI(
    title="RAGChat API",
    description="生产级RAG对话系统",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
