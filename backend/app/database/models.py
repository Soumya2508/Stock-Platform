"""
SQLAlchemy database models for stock data.

This module defines the database schema for storing:
- Stock daily data (OHLCV + calculated metrics)
- Company information

Challenges:
- Balancing normalization vs query performance
- Handling timezone-aware dates from yfinance

Future Improvements:
- Add indexes for frequently queried columns
- Partition tables by date for large datasets
"""

from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Index
from sqlalchemy.sql import func
from app.database.connection import Base


class StockData(Base):
    """
    Stores daily stock data including OHLCV and calculated metrics.
    
    Columns:
        - id: Primary key
        - symbol: Stock ticker (e.g., TCS.NS)
        - date: Trading date
        - open, high, low, close: Price data
        - volume: Trading volume
        - daily_return: (close - open) / open * 100
        - ma_7: 7-day moving average
        - ma_20: 20-day moving average
        - high_52w: 52-week high
        - low_52w: 52-week low
        - volatility: 30-day volatility score
        - momentum: Rate of change vs 20 days ago
    """
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # OHLCV data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
    # Calculated metrics
    daily_return = Column(Float)
    ma_7 = Column(Float)
    ma_20 = Column(Float)
    high_52w = Column(Float)
    low_52w = Column(Float)
    volatility = Column(Float)
    momentum = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Composite index for common queries
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date', unique=True),
    )


class Company(Base):
    """
    Stores company metadata for quick lookups.
    
    Columns:
        - symbol: Stock ticker (primary key)
        - name: Full company name
        - sector: Industry sector
        - current_price: Latest closing price
        - daily_change: Today's percentage change
    """
    __tablename__ = "companies"

    symbol = Column(String(20), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sector = Column(String(50))
    current_price = Column(Float)
    daily_change = Column(Float)
    updated_at = Column(DateTime, onupdate=func.now())
