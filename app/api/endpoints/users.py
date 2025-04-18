from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.models.user import User

router = APIRouter()


@router.get("/")
async def read_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session)
):
    """
    获取用户列表
    """
    result = await db.exec(select(User).offset(skip).limit(limit))
    users = result.all()
    return users


@router.get("/{user_id}")
async def read_user(user_id: int, db: AsyncSession  = Depends(get_async_session)):
    """
    获取特定用户
    """
    user = await db.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user