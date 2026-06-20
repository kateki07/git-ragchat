from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.user_dao import UserDao
from src.dto.user_dto import UserDto
from src.services.base_service import BaseService


class UserService(BaseService[UserDto]):
    """ユーザー管理サービス"""

    def __init__(self, db: AsyncSession):
        super().__init__(UserDao(db), UserDto)
