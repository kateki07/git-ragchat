from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.embedding import Embedding


class EmbeddingDao(BaseDao):
    """エンベディングDAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Embedding, primary_key="uuid")

    async def get_by_chunk(self, chunk_id):
        """チャンクIDでエンベディングを取得する"""
        stmt = select(Embedding).where(Embedding.chunk_id == chunk_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_collection(self, collection_id):
        """コレクションIDでエンベディング一覧を取得する"""
        stmt = select(Embedding).where(Embedding.collection_id == collection_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
