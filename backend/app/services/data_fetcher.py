"""
Stock data access service — SQLite only.

This module provides thin query wrappers over the SQLite database.
No external API calls are made. All data comes from the static
dataset that is seeded on startup.

Functions:
- get_stock_data_df: Get historical data as a DataFrame
- get_all_stocks_df: Get data for all symbols
- get_latest_price: Get latest price + daily change
- get_latest_prices_bulk: Get latest prices for all symbols
- get_company_info: Get company metadata
"""

from __future__ import annotations

import pandas as pd
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import logging

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.database.models import StockData

logger = logging.getLogger(__name__)


def get_stock_data_df(db: Session, symbol: str, days: int = 365) -> pd.DataFrame:
    """
    Load last N trading days of data for a symbol from SQLite.

    Returns a DataFrame with columns matching the StockData model.
    """
    rows = (
        db.query(StockData)
        .filter(StockData.symbol == symbol)
        .order_by(StockData.date.desc())
        .limit(days)
        .all()
    )

    if not rows:
        logger.warning(f"No data found in DB for {symbol}")
        return pd.DataFrame()

    # Convert to DataFrame
    data = []
    for r in reversed(rows):  # ascending order
        data.append({
            "symbol": r.symbol,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume,
            "daily_return": r.daily_return,
            "ma_7": r.ma_7,
            "ma_20": r.ma_20,
            "high_52w": r.high_52w,
            "low_52w": r.low_52w,
            "volatility": r.volatility,
            "momentum": r.momentum,
            "trend_strength": r.trend_strength,
        })

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_all_stocks_df(db: Session, days: int = 365) -> Dict[str, pd.DataFrame]:
    """
    Load historical data for ALL configured symbols from SQLite.

    Returns a dict mapping symbol -> DataFrame.
    """
    result = {}
    for symbol in STOCK_SYMBOLS:
        df = get_stock_data_df(db, symbol, days)
        if not df.empty:
            result[symbol] = df
    return result


def get_latest_price(db: Session, symbol: str) -> Dict:
    """
    Get the latest closing price and daily change for a symbol.

    Returns: {'current_price': float, 'daily_change': float}
    """
    rows = (
        db.query(StockData.close)
        .filter(StockData.symbol == symbol)
        .order_by(StockData.date.desc())
        .limit(2)
        .all()
    )

    if not rows:
        return {"current_price": 0.0, "daily_change": 0.0}

    current = rows[0][0]
    prev = rows[1][0] if len(rows) >= 2 else current
    change = round(((current - prev) / prev) * 100, 2) if prev else 0.0

    return {"current_price": round(current, 2), "daily_change": change}


def get_latest_prices_bulk(db: Session, symbols: List[str] = None) -> Dict[str, Dict]:
    """
    Get latest prices for multiple symbols.

    Returns: {symbol: {'current_price': float, 'daily_change': float}}
    """
    if symbols is None:
        symbols = STOCK_SYMBOLS

    return {symbol: get_latest_price(db, symbol) for symbol in symbols}


def get_company_info(symbol: str) -> Dict:
    """
    Get company metadata (name, symbol) from config.
    """
    return {
        "symbol": symbol,
        "name": COMPANY_NAMES.get(symbol, symbol.replace(".NS", "")),
    }
