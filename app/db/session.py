from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# 创建异步会话
SessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 数据库依赖项 - 异步版本
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()