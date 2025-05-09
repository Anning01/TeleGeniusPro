# After the user connects, a message is sent to the user based on the user's message or the first time
from typing import Type

from sqlmodel import select

from app.db.session import async_session_maker
from app.models import Chat, User
from app.scripts.chat import Chat as ChatScript
from app.scripts.producer import Producer


async def get_history(user_id: int, is_read: bool = False):
    async with async_session_maker() as session:
        if is_read:
            statement = (
                select(Chat.role, Chat.message)
                .where(Chat.user_id == user_id, Chat.is_read == is_read)
                .order_by(Chat.id)
            )
        else:
            statement = (
                select(Chat.role, Chat.message)
                .where(Chat.user_id == user_id)
                .order_by(Chat.id)
            )
        result = await session.execute(statement)
        chats = result.fetchall()
        # Use the map higher-order function to convert tuples into lists
        chat_list = list(map(lambda x: {"role": x[0], "content": x[1]}, chats))
        return chat_list


async def save_chat(user_id: int, role: str, message: str, is_read: bool = False):
    async with async_session_maker() as session:
        chat = Chat(user_id=user_id, role=role, message=message, is_read=is_read)
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat


async def reply_message(user: Type[User] | None):
    history = await get_history(user.id)
    if not history:
        history.append(
            {
                "role": "system",
                "content": "Ok. Now you start to say hello to the users.",
            }
        )
        await save_chat(
            user.id, "system", "Ok. Now you start to say hello to the users.", True
        )
    chat = ChatScript(history, user.meta)
    message = chat.chat_with_openai()
    await save_chat(user.id, "assistant", message)
    # After returning the message, call the generator to publish it to redis
    await Producer().send_message(user.id)
