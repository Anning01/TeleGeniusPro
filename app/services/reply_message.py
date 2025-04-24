# 用户连接后，根据用户消息或者首次，给用户发送消息
from typing import Type

from sqlmodel import select

from app.db.session import async_session_maker
from app.models import Chat, User
from app.scripts.chat import Chat as ChatScript
from app.scripts.producer import Producer


async def get_history(user_id: int):
    async with async_session_maker() as session:
        statement = select(Chat.role, Chat.message).where(Chat.user_id == user_id).order_by(Chat.id)
        result = await session.execute(statement)
        chats = result.fetchall()
        # 使用map高阶函数把元组转列表
        chat_list = list(map(lambda x: {"role": x[0], "content": x[1]}, chats))
        return chat_list

async def save_chat(user_id: int, role: str, message: str):
    async with async_session_maker() as session:
        print(message)
        chat = Chat(user_id=user_id, role=role, message=message)
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat


async def reply_message(user: Type[User] | None):
    history = await get_history(user.id)
    if not history:
        history.append({"role": "system", "content": "Ok. Now you start to say hello to the users."})
        await save_chat(user.id, "system", "Ok. Now you start to say hello to the users.")
    chat = ChatScript(history, user.meta)
    message = chat.chat_with_openai()
    await save_chat(user.id, "assistant", message)
    # 返回消息后调用生成者发布到redis
    await Producer().send_message(user.id)
