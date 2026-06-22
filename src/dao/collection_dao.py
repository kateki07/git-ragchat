from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.knowledge import Collection


class CollectionDao(BaseDao):
    """コレクションDAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Collection, primary_key="uuid")

    async def get_by_name(self, name: str):
        """名前でコレクションを取得する"""
        stmt = select(Collection).where(Collection.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
