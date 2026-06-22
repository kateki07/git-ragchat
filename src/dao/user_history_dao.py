from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.memory import UserHistory


class UserHistoryDao(BaseDao):
    """ユーザー履歴DAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, UserHistory, primary_key="id")

    async def get_by_session(self, session_id):
        """セッションIDで履歴一覧を取得する"""
        stmt = select(UserHistory).where(UserHistory.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
