from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.knowledge import File


class FileDao(BaseDao):
    """ファイルDAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, File, primary_key="uuid")

    async def get_by_collection(self, collection_id):
        """コレクションIDでファイル一覧を取得する"""
        stmt = select(File).where(File.collection_id == collection_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
