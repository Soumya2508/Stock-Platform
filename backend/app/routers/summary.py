"""
Summary API router.

Provides endpoints for stock summary statistics.

Endpoint: GET /summary/{symbol}
- Returns 52-week stats, volatility, momentum, and trend analysis
- All data served from SQLite
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
from sqlalchemy.orm import Session

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.stock_data import StockSummary
from app.database.connection import get_db
from app.services.data_fetcher import get_stock_data_df
from app.services.metrics_calculator import get_summary_stats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/{symbol}", response_model=StockSummary)
async def get_stock_summary(symbol: str, db: Session = Depends(get_db)):
    """
    Get summary statistics for a stock.

    Includes:
    - Current price and daily return
    - 52-week high and low
    - Average closing price
    - Volatility score
    - Momentum index
    - Trend strength

    Args:
        symbol: Stock ticker symbol (e.g., TCS.NS)
    """
    # Normalize symbol
    if not symbol.endswith('.NS'):
        symbol = f"{symbol}.NS"

    if symbol not in STOCK_SYMBOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found"
        )

    # Load full year from SQLite (metrics are pre-computed during seeding)
    df = get_stock_data_df(db, symbol, 365)

    if df.empty:
        raise HTTPException(
            status_code=503,
            detail=f"No data available for {symbol}"
        )

    stats = get_summary_stats(df)

    return StockSummary(
        symbol=symbol,
        name=COMPANY_NAMES.get(symbol, symbol),
        current_price=round(stats.get('current_price', 0), 2),
        daily_return=round(stats.get('daily_return', 0), 2),
        high_52w=round(stats.get('high_52w', 0), 2),
        low_52w=round(stats.get('low_52w', 0), 2),
        avg_close=round(stats.get('avg_close', 0), 2),
        avg_volume=int(stats.get('avg_volume', 0)),
        volatility=round(stats.get('volatility', 0), 2),
        momentum=round(stats.get('momentum', 0), 2),
        trend_strength=round(stats.get('trend_strength', 0), 2),
    )
