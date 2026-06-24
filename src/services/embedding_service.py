from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.embedding_dao import EmbeddingDao
from src.dto.embedding_dto import EmbeddingDto
from src.services.base_service import BaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService(BaseService[EmbeddingDto]):
    """エンベディング管理サービス"""

    def __init__(self, db: AsyncSession):
        super().__init__(EmbeddingDao(db), EmbeddingDto)
        self.dao: EmbeddingDao = self.dao

    async def batch_embedding_create(self, items: list[EmbeddingDto]) -> None:
        """エンベディングを一括挿入する"""
        await self.dao.batch_embedding_create(items)
        logger.info(f"エンベディング一括挿入完了: {len(items)}件")
