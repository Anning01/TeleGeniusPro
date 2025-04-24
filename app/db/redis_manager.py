import json
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


class RedisManager:
    _instance = None
    _redis = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init_redis(self):
        if self._redis is None:
            self._redis = await redis.from_url(
                str(settings.REDIS_URL),
                encoding="utf-8",
                decode_responses=True,
                max_connections=400,  # Limit the maximum number of connections
                retry_on_timeout=True,  # Timeout retry
                health_check_interval=30,  # Interval of health check-ups
            )

    async def close(self):
        if self._redis is not None:
            await self._redis.close()

    async def get(self, key: str) -> Optional[str]:
        await self.init_redis()
        return await self._redis.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self.init_redis()
        await self._redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self.init_redis()
        await self._redis.delete(key)

    async def rpush(self, key: str, value: list[dict]):
        await self.init_redis()
        for obj in value:
            serialized_obj = json.dumps(obj)
            await self._redis.rpush(key, serialized_obj)
            await self._redis.expire(key, 3600)

    async def lpop(self, key: str):
        await self.init_redis()
        return await self._redis.lpop(key)

    async def llen(self, key: str):
        await self.init_redis()
        return await self._redis.llen(key)

    # 删除所有key
    async def flushall(self):
        await self.init_redis()
        await self._redis.flushall()

    async def exists(self, key: str):
        await self.init_redis()
        return await self._redis.exists(key)

    async def scan_iter(self, match: str = "*"):
        await self.init_redis()
        async for key in self._redis.scan_iter(match=match):
            yield key

    async def pubsub_num_subs(self, channel: str):
        await self.init_redis()
        return await self._redis.pubsub_numsub(channel)

    async def publish(self, channel: str, message: str):
        await self.init_redis()
        await self._redis.publish(channel, message)

    async def pubsub(self):
        await self.init_redis()
        return self._redis.pubsub(ignore_subscribe_messages=True)


redis_manager = RedisManager()
