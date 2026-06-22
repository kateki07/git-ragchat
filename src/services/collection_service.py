from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.collection_dao import CollectionDao
from src.dto.collection_dto import CollectionDto
from src.services.base_service import BaseService


class CollectionService(BaseService[CollectionDto]):
    """コレクション管理サービス"""

    def __init__(self, db: AsyncSession):
        super().__init__(CollectionDao(db), CollectionDto)
