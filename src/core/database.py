import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite专用
    echo=settings.debug,  # debug模式下打印所有SQL语句
)

# 开启SQLite外键约束
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI依赖注入：每个请求获得一个独立的数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """应用启动时初始化数据库，自动建表"""
    import src.models  # noqa: F401 — 触发所有模型的注册
    Base.metadata.create_all(bind=engine)
    logger.info("数据库初始化完成")
