from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.settings import get_setting

db_settings = get_setting("db")
engine = create_async_engine(
    url=str(db_settings.DATABASE_DSN),
    pool_size=db_settings.MAX_CONNECTIONS,
    max_overflow=db_settings.MAX_OVERFLOW,
    pool_pre_ping=True,
)

AsyncLocalSession = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=True,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncLocalSession() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
