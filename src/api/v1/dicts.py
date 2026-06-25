from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.api_contract import APIContract
from src.db.pg_db import get_db
from src.services.data_dictionary_service import DataDictionaryService

router = APIRouter(tags=["dicts"], prefix="/dicts")


@router.get("/{key}")
async def get_dict(key: str, db: AsyncSession = Depends(get_db)):
    """キーで設定値を取得する"""
    dict_service = DataDictionaryService(db)
    return APIContract.success(await dict_service.get_by_key(key))


@router.post("/batch-upsert")
async def batch_upsert_dicts(items: list[dict], db: AsyncSession = Depends(get_db)):
    """データ辞書を一括新規作成または更新する"""
    dict_service = DataDictionaryService(db)
    await dict_service.batch_upsert_dicts(items)
    return APIContract.success(None)
