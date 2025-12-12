"""
Database connection and session management.

This module handles:
- SQLite database connection setup
- Async session management
- Database initialization

Challenges:
- SQLite doesn't support true async, using aiosqlite for async-like behavior
- Connection pooling is limited with SQLite

Future Improvements:
- Migrate to PostgreSQL for production
- Add connection pooling with asyncpg
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app.config import DATABASE_URL, DATABASE_PATH

# Ensure data directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)
