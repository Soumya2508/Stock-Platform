"""
Summary API router.

Provides endpoints for stock summary statistics.

Endpoint: GET /summary/{symbol}
- Returns 52-week stats, volatility, momentum, and trend analysis
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
from sqlalchemy.orm import Session

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.stock_data import StockSummary
from app.services.data_fetcher import fetch_stock_data
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics, get_summary_stats
from app.database.connection import get_db
from app.services.db_store import has_enough_data, load_stock_data_from_db, replace_symbol_history
from app.services.cache_service import (
    stock_data_cache,
    get_cached,
    set_cached
)

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
    
    cache_key = f"summary:{symbol}"
    
    # Check cache
    cached = get_cached(stock_data_cache, cache_key)
    if cached:
        return cached

    # Try DB first: summary needs ~1y data; we treat 200 rows as "good enough"
    try:
        if has_enough_data(db, symbol, minimum_rows=200):
            db_rows = load_stock_data_from_db(db, symbol, 252)
            if len(db_rows) >= 50:
                # Convert to DataFrame for reuse of existing summary logic
                df_db = {
                    'date': [r.date for r in db_rows],
                    'open': [r.open for r in db_rows],
                    'high': [r.high for r in db_rows],
                    'low': [r.low for r in db_rows],
                    'close': [r.close for r in db_rows],
                    'volume': [r.volume for r in db_rows],
                    'daily_return': [r.daily_return for r in db_rows],
                    'ma_7': [r.ma_7 for r in db_rows],
                    'ma_20': [r.ma_20 for r in db_rows],
                    'high_52w': [r.high_52w for r in db_rows],
                    'low_52w': [r.low_52w for r in db_rows],
                    'volatility': [r.volatility for r in db_rows],
                    'momentum': [r.momentum for r in db_rows],
                    'trend_strength': [r.trend_strength for r in db_rows],
                    'symbol': [r.symbol for r in db_rows],
                }
                import pandas as pd
                df = pd.DataFrame(df_db)
                stats = get_summary_stats(df)

                response = StockSummary(
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

                set_cached(stock_data_cache, cache_key, response)
                return response
    except Exception as e:
        logger.warning(f"DB summary read failed for {symbol}: {e}")
    
    # Fetch full year of data for 52-week calculations
    df = fetch_stock_data(symbol, period="1y")
    
    if df is None or df.empty:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to fetch data for {symbol}"
        )
    
    # Process data
    df = clean_stock_data(df)
    df = calculate_all_metrics(df)

    # Persist to DB (best effort)
    try:
        replace_symbol_history(db, symbol, df)
    except Exception as e:
        logger.warning(f"DB write failed for {symbol}: {e}")
    
    # Get summary stats
    stats = get_summary_stats(df)
    
    response = StockSummary(
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
        trend_strength=round(stats.get('trend_strength', 0), 2)
    )
    
    # Cache response
    set_cached(stock_data_cache, cache_key, response)
    
    return response
