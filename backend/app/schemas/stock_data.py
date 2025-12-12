"""
Pydantic schemas for Stock Data API responses.

Defines data models for stock data, summary, and comparison endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date


class StockDataPoint(BaseModel):
    """Single day of stock data."""
    date: str = Field(..., description="Trading date")
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_return: Optional[float] = None
    ma_7: Optional[float] = None
    ma_20: Optional[float] = None
    volatility: Optional[float] = None
    momentum: Optional[float] = None


class StockDataResponse(BaseModel):
    """Response for stock data endpoint."""
    symbol: str
    name: str
    days: int
    data: List[StockDataPoint]


class StockSummary(BaseModel):
    """Summary statistics for a stock."""
    symbol: str
    name: str
    current_price: float
    daily_return: float
    high_52w: float
    low_52w: float
    avg_close: float
    avg_volume: int
    volatility: float
    momentum: float
    trend_strength: float


class ComparisonPerformance(BaseModel):
    """Performance metrics for one stock in comparison."""
    total_return: float
    avg_daily_return: float
    volatility: float


class ComparisonResponse(BaseModel):
    """Response for stock comparison endpoint."""
    symbols: List[str]
    period: Dict[str, str]
    correlation: Dict[str, float]
    performance: Dict[str, ComparisonPerformance]
    chart_data: Dict[str, List]


class CorrelationMatrixResponse(BaseModel):
    """Response for correlation matrix endpoint."""
    symbols: List[str]
    matrix: List[List[float]]


class TopMover(BaseModel):
    """A top gaining or losing stock."""
    symbol: str
    name: str
    current_price: float
    daily_change: float


class TopMoversResponse(BaseModel):
    """Response for top movers endpoint."""
    date: str
    gainers: List[TopMover]
    losers: List[TopMover]
