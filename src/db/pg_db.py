import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings
from src.models.base import Base  # noqa: F401 — re-export for convenience

logger = logging.getLogger(__name__)


def get_db_url() -> str:
    return settings.database_url.replace("postgresql://", "postgresql+asyncpg://")


engine = create_async_engine(
    get_db_url(),
    pool_size=10,
    pool_recycle=3600,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI依赖注入：每个请求获得一个独立的异步数据库会话"""
    db = async_session()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库操作错误: {e}")
        if db.in_transaction():
            await db.rollback()
    finally:
        await db.close()


async def init_db():
    """应用启动时初始化数据库，自动建表"""
    import src.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库初始化完成")
