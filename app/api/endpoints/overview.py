from fastapi import APIRouter, Depends
from sqlalchemy import func, select, Integer, case
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.models.user import User
from app.models.chat import Chat

router = APIRouter()

@router.get("/overview")
async def overview(session: AsyncSession = Depends(get_async_session)):
    # 总用户数
    total_users = await session.scalar(select(func.count(User.id)))
    # 总聊天数
    total_chats = await session.scalar(select(func.count(Chat.id)))
    # AI回复数
    ai_replies = await session.scalar(select(func.count(Chat.id)).where(Chat.role == "assistant"))
    # 当前活跃用户数（回复的用户）
    active_users = await session.scalar(select(func.count(func.distinct(Chat.user_id))).where(Chat.role == "user"))
    # ai已接待用户数
    subq = select(Chat.user_id).where(Chat.role == "assistant").group_by(Chat.user_id).having(func.count(Chat.id) >= 2).subquery()
    received_users = await session.scalar(select(func.count()).select_from(subq))
    # 消息阅读率
    read_rate = await session.scalar(select(func.avg(Chat.is_read.cast(Integer))))
    # TODO:有购买意图用户数
    purchase_users = active_users // 2
    # 活跃用户占比   
    active_user_rate = active_users / total_users if total_users else 0
    # ai接待率
    received_active_rate = received_users / active_users if active_users else 0
    # AI回复占总消息比例
    ai_reply_rate = ai_replies / total_chats if total_chats else 0
    # 平均每活跃用户聊天数目
    avg_chat_per_active_user = total_chats / active_users if active_users else 0
    # 购买意图用户占比
    purchase_user_rate = purchase_users / total_users if active_users else 0
    # 购买意图 / 活跃用户占比
    purchase_active_rate = purchase_users / active_users if active_users else 0

    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "ai_replies": ai_replies,
        "active_users": active_users,
        "received_users": received_users,
        "read_rate": f"{read_rate:.2%}",
        "purchase_users": purchase_users,
        "active_user_rate": f"{active_user_rate:.2%}",
        "received_active_rate": f"{received_active_rate:.2%}",
        "ai_reply_rate": f"{ai_reply_rate:.2%}",
        "avg_chat_per_active_user": f"{avg_chat_per_active_user:.2f}",
        "purchase_user_rate": f"{purchase_user_rate:.2%}",
        "purchase_active_rate": f"{purchase_active_rate:.2%}",
    } 
