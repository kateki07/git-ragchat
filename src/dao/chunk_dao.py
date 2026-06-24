import os
from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.knowledge import Chunk
from src.utils.sql_template_manager import SQLTemplateManager


class ChunkDao(BaseDao):
    """チャンクDAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Chunk, primary_key="uuid")
        self.sql_template_manager = SQLTemplateManager(os.path.dirname(__file__))

    async def get_by_file(self, file_id):
        """ファイルIDでチャンク一覧を取得する"""
        stmt = select(Chunk).where(Chunk.file_id == file_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_file_id(self, file_id):
        """ファイルIDでチャンク一覧を取得する（インデックス順）"""
        stmt = select(Chunk).where(Chunk.file_id == file_id).order_by(Chunk.index)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_chunks_by_ids(self, chunk_ids: list):
        """複数チャンクIDでチャンク一覧を取得する"""
        stmt = select(Chunk).where(Chunk.uuid.in_(chunk_ids))
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

    async def query_embedding_chunks(self) -> list[dict]:
        """ベクトル化待ちチャンクを取得する（status=0、最大250件）"""
        sql = self.sql_template_manager.render_sql("sql/chunk_query.sql.j2")
        result = await self.db.execute(text(sql))
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]

    async def batch_update_status_by_uuids(self, uuids: list, new_status: int):
        """チャンクのステータスを一括更新する"""
        stmt = (
            update(Chunk)
            .where(Chunk.uuid.in_(uuids))
            .values(status=new_status)
            .returning(Chunk)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalars().all()

    async def delete_chunks_by_file_id(self, file_id):
        """ファイルIDに紐づくチャンクを全削除する"""
        stmt = delete(Chunk).where(Chunk.file_id == file_id)
        await self.db.execute(stmt)
        await self.db.commit()
