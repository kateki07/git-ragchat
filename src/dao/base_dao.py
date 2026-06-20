from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


class BaseDao:

    def __init__(self, db: AsyncSession, model, primary_key: str = "id"):
        """
        BaseDaoの初期化
        :param db: データベースセッション
        :param model: データベースモデル
        :param primary_key: 主キーのフィールド名、デフォルトは 'id'
        """
        self.db = db
        self.model = model
        self.primary_key = primary_key

    async def create(self, **kwargs):
        """汎用作成メソッド"""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def batch_create(self, objects: list):
        """汎用一括作成メソッド"""
        instances = [self.model(**obj.model_dump()) for obj in objects]
        self.db.add_all(instances)
        await self.db.commit()
        for instance in instances:
            await self.db.refresh(instance)
        return instances

    async def get_by_primary_key(self, key_value):
        """主キーでレコードを取得する"""
        stmt = select(self.model).where(
            getattr(self.model, self.primary_key) == key_value
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        """全レコードを取得する"""
        stmt = select(self.model)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_by_primary_key(self, key_value, **kwargs):
        """汎用更新メソッド"""
        stmt = (
            update(self.model)
            .where(getattr(self.model, self.primary_key) == key_value)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete_by_primary_key(self, key_value):
        """汎用削除メソッド"""
        stmt = delete(self.model).where(
            getattr(self.model, self.primary_key) == key_value
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return True
