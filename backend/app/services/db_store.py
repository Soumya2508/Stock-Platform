"""Database persistence helpers.

This project currently fetches data live from yfinance (with mock fallback).
This module adds optional persistence into SQLite so the backend can:
- Serve repeated requests without re-downloading the same history
- Remain functional even when yfinance is temporarily blocked

Design goals:
- Keep changes minimal and non-invasive
- Reuse existing SQLAlchemy models (StockData)
- Avoid complex migrations/upsert logic (delete+insert for one symbol is enough for 1y data)
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.database.models import StockData


_STOCKDATA_COLUMNS = [
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "daily_return",
    "ma_7",
    "ma_20",
    "high_52w",
    "low_52w",
    "volatility",
    "momentum",
    "trend_strength",
]


def _ensure_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    # pandas Timestamp / datetime
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def load_stock_data_from_db(db: Session, symbol: str, days: int) -> list[StockData]:
    """Load last N days from DB (ascending by date)."""
    rows_desc = (
        db.query(StockData)
        .filter(StockData.symbol == symbol)
        .order_by(StockData.date.desc())
        .limit(days)
        .all()
    )
    return list(reversed(rows_desc))


def get_latest_db_date(db: Session, symbol: str) -> Optional[date]:
    """Return latest stored trading date for a symbol."""
    row = (
        db.query(StockData.date)
        .filter(StockData.symbol == symbol)
        .order_by(StockData.date.desc())
        .first()
    )
    return row[0] if row else None


def replace_symbol_history(db: Session, symbol: str, df: pd.DataFrame) -> int:
    """Replace DB history for a symbol using the provided DataFrame.

    Notes:
    - This is intentionally simple: delete all rows for the symbol, then insert fresh.
    - The input df is expected to already have metrics computed.

    Returns:
        Number of rows inserted.
    """
    if df is None or df.empty:
        return 0

    df = df.copy()

    # Normalize required columns
    if "symbol" not in df.columns:
        df["symbol"] = symbol
    if "date" in df.columns:
        df["date"] = df["date"].apply(_ensure_date)

    # Keep only columns that exist in the model
    for col in _STOCKDATA_COLUMNS:
        if col not in df.columns:
            df[col] = None

    mappings = df[_STOCKDATA_COLUMNS].to_dict(orient="records")

    # Replace rows
    db.query(StockData).filter(StockData.symbol == symbol).delete(synchronize_session=False)
    db.bulk_insert_mappings(StockData, mappings)
    db.commit()

    return len(mappings)


def has_enough_data(db: Session, symbol: str, minimum_rows: int) -> bool:
    count = db.query(StockData).filter(StockData.symbol == symbol).count()
    return count >= minimum_rows
