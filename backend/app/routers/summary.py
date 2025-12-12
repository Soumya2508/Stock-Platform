"""
Summary API router.

Provides endpoints for stock summary statistics.

Endpoint: GET /summary/{symbol}
- Returns 52-week stats, volatility, momentum, and trend analysis
"""

from fastapi import APIRouter, HTTPException
import logging

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.stock_data import StockSummary
from app.services.data_fetcher import fetch_stock_data
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics, get_summary_stats
from app.services.cache_service import (
    stock_data_cache,
    get_cached,
    set_cached
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/{symbol}", response_model=StockSummary)
async def get_stock_summary(symbol: str):
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
