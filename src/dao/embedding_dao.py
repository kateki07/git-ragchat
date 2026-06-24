import json
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.embedding import Embedding
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _json_serializer(obj):
    """UUID/datetimeをJSONシリアライズする"""
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


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

    async def delete_embedding_by_file_id(self, file_id: UUID) -> None:
        """ファイルIDに紐づくエンベディングを削除する"""
        await self.db.execute(delete(Embedding).where(Embedding.file_id == file_id))
        await self.db.commit()
        logger.info(f"エンベディング削除完了: file_id={file_id}")

    async def batch_embedding_create(self, items: list) -> None:
        """エンベディングを一括挿入する"""
        data = [
            {
                "uuid": item.uuid,
                "file_id": item.file_id,
                "chunk_id": item.chunk_id,
                "collection_id": item.collection_id,
                "embedding_vector": list(item.embedding_vector),
                "cmetadata": item.cmetadata,
                "create_time": item.create_time,
            }
            for item in items
        ]

        insert_sql = text("""
            INSERT INTO embedding (uuid, file_id, chunk_id, collection_id, embedding_vector, cmetadata, create_time)
            SELECT
                (element->>'uuid')::UUID,
                (element->>'file_id')::UUID,
                (element->>'chunk_id')::UUID,
                (element->>'collection_id')::UUID,
                (element->>'embedding_vector')::VECTOR,
                (element->'cmetadata')::JSONB,
                (element->>'create_time')::TIMESTAMP WITH TIME ZONE
            FROM json_array_elements(CAST(:data AS json)) AS element
        """)

        await self.db.execute(
            insert_sql, {"data": json.dumps(data, default=_json_serializer)}
        )
        await self.db.commit()
