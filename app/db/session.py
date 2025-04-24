from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

# Create an asynchronous engine
engine = create_async_engine(str(settings.SQLMODEL_DATABASE_URI), echo=False)

# Create an asynchronous session
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Create database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Asynchronous acquisition of session
async def get_async_session():
    async with async_session_maker() as session:
        yield session
