"""
Synchronous Database Configuration for Workflow Services
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

from .config import settings

# Convert async URL to sync URL for SQLAlchemy
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Create synchronous engine
sync_engine = create_engine(SYNC_DATABASE_URL, echo=settings.DEBUG)

# Create synchronous session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base model (reuse from models.database)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get synchronous database session
    Used for workflow services that need sync database access
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a synchronous database session
    For direct usage in services
    """
    return SessionLocal()
