from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.retrieval import AiExtMessage


class AiExtMessageDao(BaseDao):
    """AI外部メッセージDAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AiExtMessage, primary_key="id")

    async def get_by_run_id(self, run_id: str):
        """run_idでメッセージを取得する"""
        stmt = select(AiExtMessage).where(AiExtMessage.run_id == run_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
