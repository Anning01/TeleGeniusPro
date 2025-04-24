# This document is a production consumer model mainly responsible for production
import asyncio
import json

from sqlmodel import select

from app.db.redis_manager import redis_manager
from app.db.session import async_session_maker
from app.models import Chat


class Producer:
    def __init__(self):
        self.redis_client = redis_manager

    async def send_message(self, user_id):
        await asyncio.sleep(1)
        if await self.sub_count(user_id):
            # 只有订阅了才发送
            async with async_session_maker() as session:
                statement = (
                    select(Chat)
                    .where(
                        Chat.user_id == int(user_id),
                        Chat.is_read == False,
                        Chat.role == "assistant",
                    )
                    .order_by(Chat.id)
                )
                result = await session.execute(statement)
                chats = result.scalars().all()
                print("-" * 100)
                print(f"Message to be sent {''.join([chat.message for chat in chats])}")
                for chat in chats:
                    await self.produce(user_id, chat.message)
                    chat.is_read = True
                    await session.commit()
                    await session.refresh(chat)

    async def produce(self, user_id, message):
        # Check if the user has any unsent assistant messages. If so, push them to the user immediately
        data = {"user_id": user_id, "message": message, "type": "message"}
        # Publish the data to a specific channel of Redis
        await self.redis_client.publish(f"channel:{user_id}", json.dumps(data))

    async def sub_count(self, user_id):
        channel = f"channel:{user_id}"
        result = await self.redis_client.pubsub_num_subs(channel)
        sub_count = result[0][1] if result else 0
        print(f"The user {user_id} is subscriptions count {sub_count}")
        return True if sub_count > 0 else False
