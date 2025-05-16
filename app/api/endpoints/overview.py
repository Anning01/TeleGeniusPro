from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, Integer, case, text
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta

from app.db.session import get_async_session
from app.models.user import User
from app.models.chat import Chat

import decimal

def convert_decimal(obj):
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

router = APIRouter()


@router.get("/summary")
async def overview_summary(session: AsyncSession = Depends(get_async_session)):
    total_users = await session.scalar(select(func.count(User.id)))
    total_chats = await session.scalar(select(func.count(Chat.id)))
    ai_replies = await session.scalar(select(func.count(Chat.id)).where(Chat.role == "assistant"))
    active_users = await session.scalar(select(func.count(func.distinct(Chat.user_id))).where(Chat.role == "user"))
    subq = select(Chat.user_id).where(Chat.role == "assistant").group_by(Chat.user_id).having(func.count(Chat.id) >= 2).subquery()
    received_users = await session.scalar(select(func.count()).select_from(subq))
    read_rate = await session.scalar(select(func.avg(Chat.is_read.cast(Integer))))
    purchase_users = active_users // 2
    active_user_rate = active_users / total_users if total_users else 0
    purchase_user_rate = purchase_users / total_users if total_users else 0
    purchase_active_rate = purchase_users / active_users if active_users else 0
    received_active_rate = received_users / active_users if active_users else 0
    ai_reply_rate = ai_replies / total_chats if total_chats else 0
    avg_chat_per_active_user = total_chats / active_users if active_users else 0
    result = {
        "total_users": total_users,
        "active_users": active_users,
        "active_user_rate": active_user_rate,
        "purchase_users": purchase_users,
        "purchase_user_rate": purchase_user_rate,
        "purchase_active_rate": purchase_active_rate,
        "received_users": received_users,
        "received_active_rate": received_active_rate,
        "ai_replies": ai_replies,
        "ai_reply_rate": ai_reply_rate,
        "total_chats": total_chats,
        "avg_chat_per_active_user": avg_chat_per_active_user,
        "read_rate": read_rate
    }
    return convert_decimal(result)


@router.get("/trend")
async def overview_trend(
    session: AsyncSession = Depends(get_async_session),
    period: str = Query("month", enum=["day", "month", "year"])
):
    # 时间分组表达式
    if period == "day":
        trunc_expr = func.to_char(func.date_trunc('day', Chat.created_at), 'YYYY-MM-DD')
    elif period == "year":
        trunc_expr = func.to_char(func.date_trunc('year', Chat.created_at), 'YYYY')
    else:
        trunc_expr = func.to_char(func.date_trunc('month', Chat.created_at), 'YYYY-MM')

    # X轴
    user_trend_result = await session.execute(
        select(
            trunc_expr.label('x'),
            func.count(func.distinct(Chat.user_id)).label('total_users')
        )
        .group_by(text('x'))
        .order_by(text('x'))
    )
    user_trend = user_trend_result.fetchall()
    x_labels = [row.x for row in user_trend]
    total_users_list = [row.total_users for row in user_trend]

    # 活跃用户趋势
    active_trend_result = await session.execute(
        select(
            trunc_expr.label('x'),
            func.count(func.distinct(Chat.user_id)).label('active_users')
        )
        .where(Chat.role == "user")
        .group_by(text('x'))
        .order_by(text('x'))
    )
    active_trend_map = {row.x: row.active_users for row in active_trend_result.fetchall()}
    active_users_list = [active_trend_map.get(x, 0) for x in x_labels]

    # 购买意图用户趋势（模拟：活跃用户/2）
    purchase_users_list = [v // 2 for v in active_users_list]

    # 活跃用户占比
    active_user_rate_list = [a / t if t else 0 for a, t in zip(active_users_list, total_users_list)]
    # 购买意图用户占比
    purchase_user_rate_list = [p / t if t else 0 for p, t in zip(purchase_users_list, total_users_list)]

    result = {
        "x": x_labels,
        "total_users": total_users_list,
        "active_users": active_users_list,
        "active_user_rate": active_user_rate_list,
        "purchase_user_rate": purchase_user_rate_list
    }
    
    return convert_decimal(result)

# ... 其他 import ...
from datetime import datetime, timedelta

@router.get("/mom")
async def overview_mom(session: AsyncSession = Depends(get_async_session)):
    now = datetime.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = this_month_start - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 本月
    total_users_this = await session.scalar(
        select(func.count(func.distinct(Chat.user_id))).where(Chat.created_at >= this_month_start)
    )
    total_chats_this = await session.scalar(
        select(func.count(Chat.id)).where(Chat.created_at >= this_month_start)
    )
    ai_replies_this = await session.scalar(
        select(func.count(Chat.id)).where(Chat.created_at >= this_month_start, Chat.role == "assistant")
    )
    active_users_this = await session.scalar(
        select(func.count(func.distinct(Chat.user_id))).where(Chat.created_at >= this_month_start, Chat.role == "user")
    )
    subq_this = select(Chat.user_id).where(Chat.created_at >= this_month_start, Chat.role == "assistant").group_by(Chat.user_id).having(func.count(Chat.id) >= 2).subquery()
    received_users_this = await session.scalar(select(func.count()).select_from(subq_this))
    read_rate_this = await session.scalar(
        select(func.avg(Chat.is_read.cast(Integer))).where(Chat.created_at >= this_month_start)
    )
    purchase_users_this = active_users_this // 2 if active_users_this else 0

    # 上月
    total_users_last = await session.scalar(
        select(func.count(func.distinct(Chat.user_id))).where(
            Chat.created_at >= last_month_start,
            Chat.created_at < this_month_start
        )
    )
    total_chats_last = await session.scalar(
        select(func.count(Chat.id)).where(
            Chat.created_at >= last_month_start,
            Chat.created_at < this_month_start
        )
    )
    ai_replies_last = await session.scalar(
        select(func.count(Chat.id)).where(
            Chat.created_at >= last_month_start,
            Chat.created_at < this_month_start,
            Chat.role == "assistant"
        )
    )
    active_users_last = await session.scalar(
        select(func.count(func.distinct(Chat.user_id))).where(
            Chat.created_at >= last_month_start,
            Chat.created_at < this_month_start,
            Chat.role == "user"
        )
    )
    subq_last = select(Chat.user_id).where(
        Chat.created_at >= last_month_start,
        Chat.created_at < this_month_start,
        Chat.role == "assistant"
    ).group_by(Chat.user_id).having(func.count(Chat.id) >= 2).subquery()
    received_users_last = await session.scalar(select(func.count()).select_from(subq_last))
    read_rate_last = await session.scalar(
        select(func.avg(Chat.is_read.cast(Integer))).where(
            Chat.created_at >= last_month_start,
            Chat.created_at < this_month_start
        )
    )
    purchase_users_last = active_users_last // 2 if active_users_last else 0
    # 本月
    ai_reply_rate_this = ai_replies_this / total_chats_this if total_chats_this else 0
    active_user_rate_this = active_users_this / total_users_this if total_users_this else 0
    received_active_rate_this = received_users_this / active_users_this if active_users_this else 0
    purchase_user_rate_this = purchase_users_this / total_users_this if total_users_this else 0
    purchase_active_rate_this = purchase_users_this / active_users_this if active_users_this else 0
    avg_chat_per_active_user_this = total_chats_this / active_users_this if active_users_this else 0

    # 上月
    ai_reply_rate_last = ai_replies_last / total_chats_last if total_chats_last else 0
    active_user_rate_last = active_users_last / total_users_last if total_users_last else 0
    received_active_rate_last = received_users_last / active_users_last if active_users_last else 0
    purchase_user_rate_last = purchase_users_last / total_users_last if total_users_last else 0
    purchase_active_rate_last = purchase_users_last / active_users_last if active_users_last else 0
    avg_chat_per_active_user_last = total_chats_last / active_users_last if active_users_last else 0

    # 环比增长率计算
    def mom(this, last):
        if last in [0, None]:
            if this in [0, None]:
                return 0
            else:
                return 1  # 或 return None，或 return float('inf')
        return (this - last) / last

    result = {
        "total_users": mom(total_users_this, total_users_last),
        "total_chats": mom(total_chats_this, total_chats_last),
        "ai_replies": mom(ai_replies_this, ai_replies_last),
        "active_users": mom(active_users_this, active_users_last),
        "received_users": mom(received_users_this, received_users_last),
        "read_rate": mom(read_rate_this, read_rate_last),
        "purchase_users": mom(purchase_users_this, purchase_users_last),
        "ai_reply_rate": mom(ai_reply_rate_this, ai_reply_rate_last),
        "active_user_rate": mom(active_user_rate_this, active_user_rate_last),
        "received_active_rate": mom(received_active_rate_this, received_active_rate_last),
        "purchase_user_rate": mom(purchase_user_rate_this, purchase_user_rate_last),
        "purchase_active_rate": mom(purchase_active_rate_this, purchase_active_rate_last),
        "avg_chat_per_active_user": mom(avg_chat_per_active_user_this, avg_chat_per_active_user_last),
    }
    return convert_decimal(result)