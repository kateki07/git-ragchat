from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.api_contract import APIContract
from src.db.pg_db import get_db
from src.services.user_servcie import UserService

router = APIRouter(tags=["user"], prefix="/user")


@router.get("/")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """全ユーザー取得"""
    user_service = UserService(db)
    users = await user_service.get_all()
    return APIContract.success(users)
