from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    """通用CRUD基类，所有DAO继承此类以复用基础操作"""

    def __init__(self, db: AsyncSession, model):
        self.db = db
        self.model = model

    async def get_all(self) -> list:
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def delete(self, obj) -> None:
        await self.db.delete(obj)
        await self.db.commit()
