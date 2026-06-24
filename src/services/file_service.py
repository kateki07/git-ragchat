from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.file_dao import FileDao
from src.dto.file_dto import FileDto
from src.services.base_service import BaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileService(BaseService[FileDto]):
    """ファイル管理サービス"""

    def __init__(self, db: AsyncSession):
        super().__init__(FileDao(db), FileDto)
        self.dao: FileDao = self.dao

    async def query_files(self, collection_id: Optional[str] = None) -> list[dict]:
        """コレクションIDでファイル一覧を取得する"""
        try:
            return await self.dao.query_files(collection_id)
        except Exception as e:
            logger.error(f"ファイル一覧取得に失敗しました: {e}")
            raise
