"""
Compare API router.

Provides endpoints for comparing stock performance.

Endpoint: GET /compare
- Compares two stocks' performance with correlation analysis
"""

from fastapi import APIRouter, HTTPException, Query
import logging

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.stock_data import ComparisonResponse, CorrelationMatrixResponse
from app.services.data_fetcher import fetch_stock_data
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics
from app.services.correlation import compare_stocks, generate_correlation_matrix
from app.services.cache_service import (
    stock_data_cache,
    get_cached,
    set_cached
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compare", tags=["Comparison"])


@router.get("", response_model=ComparisonResponse)
async def compare_two_stocks(
    symbol1: str = Query(..., description="First stock symbol"),
    symbol2: str = Query(..., description="Second stock symbol")
):
    """
    Compare two stocks' performance.
    
    Returns:
    - Price and returns correlation
    - Total return comparison
    - Volatility comparison
    - Normalized chart data for overlay
    
    Args:
        symbol1: First stock ticker (e.g., TCS.NS)
        symbol2: Second stock ticker (e.g., INFY.NS)
    """
    # Normalize symbols
    if not symbol1.endswith('.NS'):
        symbol1 = f"{symbol1}.NS"
    if not symbol2.endswith('.NS'):
        symbol2 = f"{symbol2}.NS"
    
    # Validate symbols
    for symbol in [symbol1, symbol2]:
        if symbol not in STOCK_SYMBOLS:
            raise HTTPException(
                status_code=404,
                detail=f"Stock {symbol} not found"
            )
    
    if symbol1 == symbol2:
        raise HTTPException(
            status_code=400,
            detail="Please select two different stocks to compare"
        )
    
    cache_key = f"compare:{symbol1}:{symbol2}"
    
    # Check cache
    cached = get_cached(stock_data_cache, cache_key)
    if cached:
        return cached
    
    # Fetch data for both stocks
    df1 = fetch_stock_data(symbol1, period="1y")
    df2 = fetch_stock_data(symbol2, period="1y")
    
    if df1 is None or df2 is None:
        raise HTTPException(
            status_code=503,
            detail="Unable to fetch stock data"
        )
    
    # Process data
    df1 = clean_stock_data(df1)
    df2 = clean_stock_data(df2)
    df1 = calculate_all_metrics(df1)
    df2 = calculate_all_metrics(df2)
    
    # Compare stocks
    comparison = compare_stocks(df1, df2, symbol1, symbol2)
    
    if 'error' in comparison:
        raise HTTPException(
            status_code=400,
            detail=comparison['error']
        )
    
    response = ComparisonResponse(**comparison)
    
    # Cache response
    set_cached(stock_data_cache, cache_key, response)
    
    return response


@router.get("/correlation-matrix", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix():
    """
    Get correlation matrix for all stocks.
    
    Returns a matrix showing correlation coefficients between
    all pairs of stocks based on daily returns.
    
    Useful for portfolio diversification analysis.
    """
    cache_key = "correlation_matrix"
    
    # Check cache
    cached = get_cached(stock_data_cache, cache_key)
    if cached:
        return cached
    
    # Fetch data for all stocks
    stock_data = {}
    
    for symbol in STOCK_SYMBOLS:
        df = fetch_stock_data(symbol, period="1y")
        if df is not None:
            df = clean_stock_data(df)
            df = calculate_all_metrics(df)
            stock_data[symbol] = df
    
    if len(stock_data) < 2:
        raise HTTPException(
            status_code=503,
            detail="Insufficient data to generate correlation matrix"
        )
    
    # Generate matrix
    matrix_data = generate_correlation_matrix(stock_data)
    
    if 'error' in matrix_data:
        raise HTTPException(
            status_code=400,
            detail=matrix_data['error']
        )
    
    response = CorrelationMatrixResponse(**matrix_data)
    
    # Cache response
    set_cached(stock_data_cache, cache_key, response)
    
    return response
