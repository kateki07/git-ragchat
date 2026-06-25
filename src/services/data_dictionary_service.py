from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.data_dictionary_dao import DataDictionaryDao
from src.dto.data_dict_dto import DataDictDto
from src.services.base_service import BaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataDictionaryService(BaseService[DataDictDto]):
    """データ辞書管理サービス"""

    def __init__(self, db: AsyncSession):
        super().__init__(DataDictionaryDao(db), DataDictDto)
        self.dao: DataDictionaryDao = self.dao

    async def get_by_key(self, key: str) -> DataDictDto | None:
        """キーで設定値を取得する"""
        result = await self.dao.get_by_key(key)
        if result:
            logger.info(f"データ辞書取得: {result}")
            return DataDictDto.model_validate(result)
        return None

    async def batch_upsert_dicts(self, items: list[dict]) -> None:
        """データ辞書を一括新規作成または更新する"""
        await self.dao.batch_upsert_dicts(items)
