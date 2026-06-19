from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.user import User


class UserDao(BaseDao):

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
