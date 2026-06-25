from sqlalchemy import select, update
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

    async def batch_upsert_dicts(self, items: list[dict]):
        """データ辞書を一括新規作成または更新する"""
        for item in items:
            query = (
                update(DataDictionary)
                .where(DataDictionary.key == item["key"])
                .values(value=item["value"])
                .returning(DataDictionary.id)
            )
            result = await self.db.execute(query)
            if result.scalar_one_or_none() is None:
                self.db.add(DataDictionary(key=item["key"], value=item["value"]))
        await self.db.commit()
