from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.setting import DataDictionary


class DataDictionaryDao(BaseDao):
    """データ辞書DAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, DataDictionary, primary_key="id")

    async def get_by_key(self, key: str):
        """キーで設定値を取得する"""
        stmt = select(DataDictionary).where(DataDictionary.key == key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
