from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData, Integer, Column
from sqlalchemy.pool import NullPool

from .config import get_settings


settings = get_settings()

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True, nullable=False)


engine_kwargs: dict = {
    "echo": False,
    "future": True,
    "pool_pre_ping": settings.DB_POOL_PRE_PING,
}

# With this:
_is_neon = (
    settings.DATABASE_URL is not None
    and "neon.tech" in (settings.DATABASE_URL or "")
)

engine_kwargs: dict = {
    "echo": False,
    "future": True,
    "pool_pre_ping": settings.DB_POOL_PRE_PING,
    # asyncpg needs ssl passed as connect_args, NOT as a URL query param
    **({"connect_args": {"ssl": "require"}} if _is_neon else {}),
}

if settings.DB_POOL_SIZE <= 0:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_timeout"] = settings.DB_POOL_TIMEOUT_SECONDS
    engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE_SECONDS

engine: AsyncEngine = create_async_engine(
    settings.sqlalchemy_database_uri_async,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """
    Create all tables on startup.

    Note: this project can also use Alembic migrations for schema changes
    after initial table creation.
    """
    if settings.ENVIRONMENT.lower() != "development":
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

