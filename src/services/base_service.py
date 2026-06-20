import logging
from typing import List, Type, TypeVar, Generic, Optional
from pydantic import BaseModel
from src.dao.base_dao import BaseDao

logger = logging.getLogger(__name__)

DTOType = TypeVar("DTOType", bound=BaseModel)


class BaseService(Generic[DTOType]):

    def __init__(self, dao: BaseDao, dto_class: Type[DTOType]):
        """
        BaseServiceの初期化
        :param dao: データアクセスオブジェクト (DAO)
        :param dto_class: データ転送オブジェクト (DTO) クラス
        """
        self.dao = dao
        self.dto_class = dto_class

    async def create(self, **kwargs) -> DTOType:
        """汎用作成メソッド"""
        try:
            instance = await self.dao.create(**kwargs)
            return self.dto_class.model_validate(instance)
        except Exception as e:
            logger.error(f"作成処理に失敗しました: {e}")
            raise

    async def batch_create(self, objects: List[DTOType]) -> List[DTOType]:
        """一括作成メソッド"""
        try:
            instances = await self.dao.batch_create(objects)
            return [self.dto_class.model_validate(instance) for instance in instances]
        except Exception as e:
            logger.error(f"一括作成処理に失敗しました: {e}")
            raise

    async def get_by_id(self, id) -> Optional[DTOType]:
        """主キーでレコードを取得する"""
        try:
            instance = await self.dao.get_by_primary_key(id)
            if instance:
                return self.dto_class.model_validate(instance)
            return None
        except Exception as e:
            logger.error(f"取得処理に失敗しました: id={id}, error={e}")
            raise

    async def get_all(self) -> List[DTOType]:
        """全レコードを取得する"""
        try:
            instances = await self.dao.get_all()
            if instances:
                return [self.dto_class.model_validate(instance) for instance in instances]
            return []
        except Exception as e:
            logger.error(f"全件取得処理に失敗しました: {e}")
            raise

    async def update_by_id(self, id, **kwargs) -> Optional[DTOType]:
        """汎用更新メソッド"""
        try:
            instance = await self.dao.update_by_primary_key(id, **kwargs)
            if instance:
                return self.dto_class.model_validate(instance)
            return None
        except Exception as e:
            logger.error(f"更新処理に失敗しました: id={id}, error={e}")
            raise

    async def delete_by_id(self, id) -> bool:
        """汎用削除メソッド"""
        try:
            existing = await self.dao.get_by_primary_key(id)
            if existing is None:
                logger.warning(f"削除対象のレコードが見つかりません: id={id}")
                return False
            return await self.dao.delete_by_primary_key(id)
        except Exception as e:
            logger.error(f"削除処理に失敗しました: id={id}, error={e}")
            raise
