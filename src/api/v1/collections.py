import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.api_contract import APIContract
from src.db.pg_db import get_db
from src.services.collection_service import CollectionService

router = APIRouter(tags=["collections"], prefix="/collections")


@router.post("/")
async def create(data: dict, db: AsyncSession = Depends(get_db)):
    """コレクション作成"""
    service = CollectionService(db)
    return APIContract.success(
        await service.create(
            name=data.get("name"),
            uuid=uuid.uuid1(),
            create_time=datetime.now(timezone.utc),
        )
    )


@router.put("/{uuid}")
async def update(uuid: str, data: dict, db: AsyncSession = Depends(get_db)):
    """コレクション更新"""
    service = CollectionService(db)
    return APIContract.success(await service.update_by_id(uuid, name=data.get("name")))


@router.get("/{uuid}")
async def get_by_id(uuid: str, db: AsyncSession = Depends(get_db)):
    """コレクション取得"""
    service = CollectionService(db)
    return APIContract.success(await service.get_by_id(uuid))


@router.get("/")
async def get_all(db: AsyncSession = Depends(get_db)):
    """コレクション一覧取得"""
    service = CollectionService(db)
    return APIContract.success(await service.get_all())


@router.delete("/{uuid}")
async def delete(uuid: str, db: AsyncSession = Depends(get_db)):
    """コレクション削除"""
    service = CollectionService(db)
    return APIContract.success(await service.delete(uuid))
