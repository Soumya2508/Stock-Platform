"""
Stock Data API router.

Provides endpoints for retrieving historical stock data.

Endpoint: GET /data/{symbol}
- Returns historical OHLCV data with calculated metrics
- All data served from SQLite (seeded from static JSON)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
import logging
from sqlalchemy.orm import Session

from app.config import STOCK_SYMBOLS, COMPANY_NAMES, DEFAULT_DAYS
from app.schemas.stock_data import StockDataResponse, StockDataPoint
from app.database.connection import get_db
from app.services.data_fetcher import get_stock_data_df

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["Stock Data"])


@router.get("/{symbol}", response_model=StockDataResponse)
async def get_stock_data(
    symbol: str,
    days: int = Query(DEFAULT_DAYS, ge=7, le=365, description="Number of days of data"),
    db: Session = Depends(get_db),
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

    # Read from SQLite
    df = get_stock_data_df(db, symbol, days)

    if df.empty:
        raise HTTPException(
            status_code=503,
            detail=f"No data available for {symbol}. Database may need seeding."
        )

    # Convert to response format
    data_points = []
    for _, row in df.iterrows():
        point = StockDataPoint(
            date=str(row['date'].date()) if hasattr(row['date'], 'date') else str(row['date']).split()[0],
            open=round(row['open'], 2),
            high=round(row['high'], 2),
            low=round(row['low'], 2),
            close=round(row['close'], 2),
            volume=int(row['volume']),
            daily_return=round(row.get('daily_return', 0) or 0, 2),
            ma_7=round(row.get('ma_7', 0) or 0, 2),
            ma_20=round(row.get('ma_20', 0) or 0, 2),
            volatility=round(row.get('volatility', 0) or 0, 2),
            momentum=round(row.get('momentum', 0) or 0, 2),
        )
        data_points.append(point)

    return StockDataResponse(
        symbol=symbol,
        name=COMPANY_NAMES.get(symbol, symbol),
        days=len(data_points),
        data=data_points,
    )


@router.get("/{symbol}/analytics/moving-average", tags=["Analytics"])
async def get_moving_average(
    symbol: str, 
    days: int = Query(7, ge=1, le=200, description="Moving average window size"),
    db: Session = Depends(get_db)
):
    """
    Compute moving average natively from the SQLite database.
    """
    if not symbol.endswith('.NS'):
        symbol = f"{symbol}.NS"
        
    df = get_stock_data_df(db, symbol, 365)
    
    if df.empty:
        raise HTTPException(
            status_code=503,
            detail=f"No data available to compute moving average for {symbol}."
        )
        
    # Sort by date ascending to compute rolling mean
    df = df.sort_values(by="date")
    df[f"ma_{days}"] = df["close"].rolling(window=days, min_periods=1).mean()
    
    # Return latest configured days point to reduce payload, ordered desc
    df = df.sort_values(by="date", ascending=False).head(30)
    
    results = []
    for _, row in df.iterrows():
        results.append({
            "date": str(row['date'].date()) if hasattr(row['date'], 'date') else str(row['date']).split()[0],
            "close": round(row['close'], 2),
            f"ma_{days}": round(row[f"ma_{days}"], 2)
        })
        
    return {
        "symbol": symbol,
        "window": days,
        "data": results
    }
