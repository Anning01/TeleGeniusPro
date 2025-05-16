from fastapi import APIRouter, Depends
from sqlalchemy import func, select, Integer, case, text
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta

from app.db.session import get_async_session
from app.models.user import User
from app.models.chat import Chat

router = APIRouter()

@router.get("/overview")
async def overview(session: AsyncSession = Depends(get_async_session)):
    # 总用户数
    total_users = await session.scalar(select(func.count(User.id)))
    # 按天统计用户增长趋势（最近7天）
    user_trend = await session.execute(
        select(
            func.date_trunc('day', Chat.created_at).label('date'),
            func.count(func.distinct(Chat.user_id)).label('count')
        )
        .where(Chat.created_at >= datetime.now() - timedelta(days=7))
        .group_by(text('date'))
        .order_by(text('date'))
    )
    user_trend = [(row.date.strftime('%Y-%m-%d'), row.count) for row in user_trend.fetchall()]

    # 总聊天数
    total_chats = await session.scalar(select(func.count(Chat.id)))
    # AI回复数
    ai_replies = await session.scalar(select(func.count(Chat.id)).where(Chat.role == "assistant"))
    
    # 当前活跃用户数（回复的用户）
    active_users = await session.scalar(select(func.count(func.distinct(Chat.user_id))).where(Chat.role == "user"))
    # 按天统计活跃用户趋势（最近7天）
    active_trend = await session.execute(
        select(
            func.date_trunc('day', Chat.created_at).label('date'),
            func.count(func.distinct(Chat.user_id)).label('count')
        )
        .where(Chat.role == "user")
        .where(Chat.created_at >= datetime.now() - timedelta(days=7))
        .group_by(text('date'))
        .order_by(text('date'))
    )
    active_trend = [(row.date.strftime('%Y-%m-%d'), row.count) for row in active_trend.fetchall()]
    
    # ai已接待用户数
    subq = select(Chat.user_id).where(Chat.role == "assistant").group_by(Chat.user_id).having(func.count(Chat.id) >= 2).subquery()
    received_users = await session.scalar(select(func.count()).select_from(subq))
    # 消息阅读率
    read_rate = await session.scalar(select(func.avg(Chat.is_read.cast(Integer))))
    # TODO:有购买意图用户数
    purchase_users = active_users // 2
    # 按天统计购买意图用户趋势（最近7天，这里仍用模拟数据）
    purchase_trend = [(date, count//2) for date, count in active_trend]
    
    # 活跃用户占比
    active_user_rate = active_users / total_users if total_users else 0
    # 按天统计活跃用户占比趋势
    active_rate_trend = []
    for i, (date, active_count) in enumerate(active_trend):
        total_count = user_trend[i][1] if i < len(user_trend) else total_users
        rate = active_count / total_count if total_count else 0
        active_rate_trend.append((date, rate))
    
    # ai接待率
    received_active_rate = received_users / active_users if active_users else 0
    # AI回复占总消息比例
    ai_reply_rate = ai_replies / total_chats if total_chats else 0
    # 平均每活跃用户聊天数目
    avg_chat_per_active_user = total_chats / active_users if active_users else 0
    # 购买意图用户占比
    purchase_user_rate = purchase_users / total_users if total_users else 0
    # 按天统计购买意图用户占比趋势
    purchase_rate_trend = []
    for i, (date, purchase_count) in enumerate(purchase_trend):
        total_count = user_trend[i][1] if i < len(user_trend) else total_users
        rate = purchase_count / total_count if total_count else 0
        purchase_rate_trend.append((date, rate))

    return {
        "total_users": {
            "current": total_users,
            "trend": user_trend
        },
        "total_chats": total_chats,
        "ai_replies": ai_replies,
        "active_users": {
            "current": active_users,
            "trend": active_trend
        },
        "received_users": received_users,
        "read_rate": read_rate,
        "purchase_users": {
            "current": purchase_users,
            "trend": purchase_trend
        },
        "active_user_rate": {
            "current": active_user_rate,
            "trend": active_rate_trend
        },
        "received_active_rate": received_active_rate,
        "ai_reply_rate": ai_reply_rate,
        "avg_chat_per_active_user": avg_chat_per_active_user,
        "purchase_user_rate": {
            "current": purchase_user_rate,
            "trend": purchase_rate_trend
        }
    } 
