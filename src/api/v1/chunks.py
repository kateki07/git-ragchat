from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.api_contract import APIContract
from src.db.pg_db import get_db
from src.services.chunk_service import ChunkService

router = APIRouter(tags=["chunks"], prefix="/chunks")


@router.get("/file/{file_id}")
async def get_chunks_by_file_id(file_id: str, db: AsyncSession = Depends(get_db)):
    """ファイルIDでチャンク一覧を取得する"""
    chunk_service = ChunkService(db)
    return APIContract.success(await chunk_service.get_chunks_by_file_id(file_id))
