"""
Stock Data API router.

Provides endpoints for retrieving historical stock data.

Endpoint: GET /data/{symbol}
- Returns historical OHLCV data with calculated metrics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.config import STOCK_SYMBOLS, COMPANY_NAMES, DEFAULT_DAYS
from app.schemas.stock_data import StockDataResponse, StockDataPoint
from app.services.data_fetcher import fetch_stock_data
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics
from app.services.cache_service import (
    stock_data_cache,
    get_cached,
    set_cached
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["Stock Data"])


@router.get("/{symbol}", response_model=StockDataResponse)
async def get_stock_data(
    symbol: str,
    days: int = Query(DEFAULT_DAYS, ge=7, le=365, description="Number of days of data")
):
    """
    Get historical stock data for a symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., TCS.NS)
        days: Number of days of data to return (7-365)
    
    Returns:
        Historical OHLCV data with calculated metrics
    """
    # Normalize symbol
    if not symbol.endswith('.NS'):
        symbol = f"{symbol}.NS"
    
    if symbol not in STOCK_SYMBOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found. Available stocks: {', '.join(STOCK_SYMBOLS)}"
        )
    
    cache_key = f"stock_data:{symbol}:{days}"
    
    # Check cache
    cached = get_cached(stock_data_cache, cache_key)
    if cached:
        return cached
    
    # Fetch data
    df = fetch_stock_data(symbol)
    
    if df is None or df.empty:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to fetch data for {symbol}. Please try again later."
        )
    
    # Clean data
    df = clean_stock_data(df)
    
    # Calculate metrics
    df = calculate_all_metrics(df)
    
    # Get last N days
    df = df.tail(days)
    
    # Convert to response format
    data_points = []
    for _, row in df.iterrows():
        point = StockDataPoint(
            # Ensure date is strictly YYYY-MM-DD string
            date=str(row['date'].date()) if hasattr(row['date'], 'date') else str(row['date']).split()[0],
            open=round(row['open'], 2),
            high=round(row['high'], 2),
            low=round(row['low'], 2),
            close=round(row['close'], 2),
            volume=int(row['volume']),
            daily_return=round(row.get('daily_return', 0), 2),
            ma_7=round(row.get('ma_7', 0), 2),
            ma_20=round(row.get('ma_20', 0), 2),
            volatility=round(row.get('volatility', 0), 2),
            momentum=round(row.get('momentum', 0), 2)
        )
        data_points.append(point)
    
    response = StockDataResponse(
        symbol=symbol,
        name=COMPANY_NAMES.get(symbol, symbol),
        days=len(data_points),
        data=data_points
    )
    
    # Cache response
    set_cached(stock_data_cache, cache_key, response)
    
    return response
