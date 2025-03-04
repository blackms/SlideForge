"""
Database session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from slideforge.core.config import settings

# Create SQLAlchemy engine for synchronous operations
engine = create_engine(
    settings.database_uri,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Create session factory for synchronous operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create async engine for async operations (if using aiosqlite or asyncpg)
if settings.database_uri.startswith("sqlite"):
    # SQLite needs special handling for async operations
    async_database_uri = settings.database_uri.replace("sqlite", "sqlite+aiosqlite")
else:
    # For PostgreSQL, we use asyncpg
    async_database_uri = settings.database_uri.replace("postgresql", "postgresql+asyncpg")

async_engine = create_async_engine(
    async_database_uri,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Create session factory for async operations
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine,
)


def get_db():
    """
    Dependency function to get a database session for synchronous operations.
    Use with FastAPI's Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """
    Dependency function to get an async database session.
    Use with FastAPI's Depends.
    """
    async with AsyncSessionLocal() as session:
        yield session
