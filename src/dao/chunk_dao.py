from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.knowledge import Chunk


class ChunkDao(BaseDao):
    """チャンクDAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Chunk, primary_key="uuid")

    async def get_by_file(self, file_id):
        """ファイルIDでチャンク一覧を取得する"""
        stmt = select(Chunk).where(Chunk.file_id == file_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def bulk_create(self, file_id, file_name: str, texts: list[str]):
        """複数チャンクを一括作成する"""
        chunks = [
            Chunk(file_id=file_id, file_name=file_name, context=text, index=i, status=0)
            for i, text in enumerate(texts)
        ]
        self.db.add_all(chunks)
        await self.db.commit()
        for chunk in chunks:
            await self.db.refresh(chunk)
        return chunks
