"""
Database connection and session management.

This module handles:
- SQLite database connection setup
- Session management
- Database initialization + auto-seeding from JSON
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging

from app.config import DATABASE_URL, DATABASE_PATH

logger = logging.getLogger(__name__)

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
    Initialize the database:
      1. Create all tables
      2. Run lightweight migrations
      3. Auto-seed from stocks.json if DB is empty
    """
    # Ensure model modules are imported so they register with Base.metadata
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Lightweight SQLite migration: add columns if older DB exists.
    try:
        with engine.begin() as conn:
            cols = conn.execute(text("PRAGMA table_info('stock_data')")).fetchall()
            col_names = {row[1] for row in cols}
            if 'trend_strength' not in col_names:
                conn.execute(text('ALTER TABLE stock_data ADD COLUMN trend_strength FLOAT'))
    except Exception:
        pass

    # Auto-seed: if stock_data table is empty, load from stocks.json
    from app.services.seed import seed_from_json
    db = SessionLocal()
    try:
        seed_from_json(db)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
    finally:
        db.close()
