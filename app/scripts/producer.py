# 此文件为生产消费者模型 主要负责生产
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
        print(await self.sub_count(user_id))
        if await self.sub_count(user_id):
            print("订阅了")
            # 只有订阅了才发送
            async with async_session_maker() as session:
                statement = select(Chat).where(Chat.user_id == int(user_id), Chat.is_read == False, Chat.role == 'assistant').order_by(Chat.id)
                result = await session.execute(statement)
                chats = result.scalars().all()
                print("-"*100)
                print(chats)
                for chat in chats:
                    await self.produce(user_id, chat.message)
                    chat.is_read = True
                    await session.commit()
                    await session.refresh(chat)

    async def produce(self, user_id, message):
        # 查询用户是否存在还未发送的assistant消息，如果有，则立马推送给用户
        data = {"user_id": user_id, "message": message, "type": "message"}
        # 将数据发布到 Redis 的特定频道
        await self.redis_client.publish(f"channel:{user_id}", json.dumps(data))

    async def sub_count(self, user_id):
        channel = f"channel:{user_id}"
        result = await self.redis_client.pubsub_num_subs(channel)
        sub_count = result[0][1] if result else 0
        return True if sub_count > 0 else False

