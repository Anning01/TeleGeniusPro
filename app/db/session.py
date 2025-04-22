from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings


# 创建异步引擎
engine = create_async_engine(
    str(settings.SQLMODEL_DATABASE_URI),
    echo=settings.DEBUG
)

# 创建异步会话
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# 数据库依赖项 - 异步版本
async def init_db():
    async with engine.begin() as conn:
        # 创建数据库表
        await conn.run_sync(SQLModel.metadata.create_all)

# 异步获取会话
async def get_async_session():
    async with async_session_maker() as session:
        yield session
