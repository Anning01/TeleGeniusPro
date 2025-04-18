from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

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
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# 异步获取会话
async def get_async_session():
    async with SessionLocal() as session:
        yield session

if __name__ == '__main__':
    init_db()