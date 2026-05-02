"""
Database seeding module.

Loads the static dataset from /data/stocks.json into SQLite
on first startup (or whenever the DB is empty).

This guarantees data availability on every deployment,
even when SQLite is ephemeral (e.g., on Vercel / Render).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.config import STOCKS_JSON_PATH, COMPANY_NAMES, COMPANY_SECTORS
from app.database.models import StockData, Company
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics

logger = logging.getLogger(__name__)


def _load_json() -> list[dict]:
    """Load raw records from the static JSON file."""
    with open(STOCKS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _seed_stock_data(db: Session) -> int:
    """Load stocks.json, compute metrics, and bulk-insert into stock_data table."""
    raw = _load_json()
    df = pd.DataFrame(raw)

    total_inserted = 0
    try:
        for symbol, group_df in df.groupby("symbol"):
            group_df = group_df.copy()
            group_df["date"] = pd.to_datetime(group_df["date"])
            group_df = clean_stock_data(group_df)
            group_df = calculate_all_metrics(group_df)

            # Prepare records for bulk insert
            cols = [
                "symbol", "date", "open", "high", "low", "close", "volume",
                "daily_return", "ma_7", "ma_20", "high_52w", "low_52w",
                "volatility", "momentum", "trend_strength",
            ]
            for col in cols:
                if col not in group_df.columns:
                    group_df[col] = None

            # Convert date to Python date objects
            group_df["date"] = group_df["date"].dt.date

            mappings = group_df[cols].to_dict(orient="records")
            db.bulk_insert_mappings(StockData, mappings)
            total_inserted += len(mappings)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error during bulk generation/insert: {e}")
        raise e

    return total_inserted


def _seed_companies(db: Session) -> int:
    """Seed the companies table from config + latest prices in stock_data."""
    count = 0
    for symbol, name in COMPANY_NAMES.items():
        # Get latest 2 closes for daily_change calculation
        rows = (
            db.query(StockData.close)
            .filter(StockData.symbol == symbol)
            .order_by(StockData.date.desc())
            .limit(2)
            .all()
        )

        current_price = rows[0][0] if rows else 0.0
        prev_price = rows[1][0] if len(rows) >= 2 else current_price
        daily_change = round(((current_price - prev_price) / prev_price) * 100, 2) if prev_price else 0.0

        company = Company(
            symbol=symbol,
            name=name,
            sector=COMPANY_SECTORS.get(symbol, "General"),
            current_price=round(current_price, 2),
            daily_change=daily_change,
        )
        db.merge(company)  # upsert
        count += 1

    db.commit()
    return count


def seed_from_json(db: Session) -> None:
    """
    Seed SQLite from stocks.json if the database is empty.

    Called automatically during application startup.
    """
    # Check if stock_data table has any rows
    row_count = db.query(StockData).count()
    if row_count > 0:
        logger.info(f"Database already has {row_count} stock records, skipping seed.")
        return

    logger.info("Database is empty. Seeding from stocks.json ...")

    stock_count = _seed_stock_data(db)
    logger.info(f"Seeded {stock_count} stock data records.")

    company_count = _seed_companies(db)
    logger.info(f"Seeded {company_count} company records.")

    logger.info("Database seeding complete.")
