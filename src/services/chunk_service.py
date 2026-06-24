from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.chunk_dao import ChunkDao
from src.dto.chunk_dto import ChunkDto
from src.dto.chunk_embedding_dto import ChunkEmbeddingDto
from src.services.base_service import BaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChunkService(BaseService[ChunkDto]):
    """チャンク管理サービス"""

    def __init__(self, db: AsyncSession):
        super().__init__(ChunkDao(db), ChunkDto)
        self.dao: ChunkDao = self.dao

    async def get_chunks_by_file_id(self, file_id: UUID) -> list[ChunkDto]:
        """ファイルIDでチャンク一覧を取得する"""
        chunks = await self.dao.get_by_file_id(file_id)
        return [
            ChunkDto(
                uuid=chunk.uuid,
                file_id=chunk.file_id,
                file_name=chunk.file_name,
                context=chunk.context,
                index=chunk.index,
                status=chunk.status,
                create_time=chunk.create_time,
            )
            for chunk in chunks
        ]

    async def get_chunks_by_ids(self, chunk_ids: list[UUID]) -> list[ChunkDto]:
        """複数チャンクIDでチャンク一覧を取得する"""
        chunks = await self.dao.get_chunks_by_ids(chunk_ids)
        return [
            ChunkDto(
                uuid=chunk.uuid,
                file_id=chunk.file_id,
                file_name=chunk.file_name,
                context=chunk.context,
                index=chunk.index,
                status=chunk.status,
                create_time=chunk.create_time,
            )
            for chunk in chunks
        ]

    async def query_embedding_chunks(self) -> list[ChunkEmbeddingDto] | None:
        """ベクトル化待ちチャンクを取得する（status=0）"""
        results = await self.dao.query_embedding_chunks()
        if results:
            return [ChunkEmbeddingDto.model_validate(result) for result in results]
        return None

    async def batch_update_status_by_uuids(self, uuids: list[UUID], new_status: int) -> None:
        """チャンクのステータスを一括更新する"""
        results = await self.dao.batch_update_status_by_uuids(uuids, new_status)
        logger.info(f"ステータス一括更新完了: {len(results)}件 → status={new_status}")

    async def delete_chunks_by_file_id(self, file_id: UUID) -> None:
        """ファイルIDに紐づくチャンクを削除する"""
        await self.dao.delete_chunks_by_file_id(file_id)
        logger.info(f"チャンク削除完了: file_id={file_id}")
