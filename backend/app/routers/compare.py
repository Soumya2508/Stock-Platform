"""
Compare API router.

Provides endpoints for comparing stock performance.

Endpoints:
- GET /compare — Compare two stocks with correlation analysis
- GET /compare/correlation-matrix — Full correlation matrix
- All data served from SQLite
"""

from fastapi import APIRouter, HTTPException, Query, Depends
import logging
from sqlalchemy.orm import Session

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.stock_data import ComparisonResponse, CorrelationMatrixResponse
from app.database.connection import get_db
from app.services.data_fetcher import get_stock_data_df, get_all_stocks_df
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics
from app.services.correlation import compare_stocks, generate_correlation_matrix

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compare", tags=["Comparison"])


@router.get("", response_model=ComparisonResponse)
async def compare_two_stocks(
    symbol1: str = Query(..., description="First stock symbol"),
    symbol2: str = Query(..., description="Second stock symbol"),
    db: Session = Depends(get_db),
):
    """
    Compare two stocks' performance.

    Returns:
    - Price and returns correlation
    - Total return comparison
    - Volatility comparison
    - Normalized chart data for overlay
    """
    # Normalize symbols
    if not symbol1.endswith('.NS'):
        symbol1 = f"{symbol1}.NS"
    if not symbol2.endswith('.NS'):
        symbol2 = f"{symbol2}.NS"

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

    # Read from SQLite
    df1 = get_stock_data_df(db, symbol1, 365)
    df2 = get_stock_data_df(db, symbol2, 365)

    if df1.empty or df2.empty:
        raise HTTPException(
            status_code=503,
            detail="Insufficient data for comparison"
        )

    comparison = compare_stocks(df1, df2, symbol1, symbol2)

    if 'error' in comparison:
        raise HTTPException(
            status_code=400,
            detail=comparison['error']
        )

    return ComparisonResponse(**comparison)


@router.get("/correlation-matrix", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(db: Session = Depends(get_db)):
    """
    Get correlation matrix for all stocks.

    Returns a matrix showing correlation coefficients between
    all pairs of stocks based on daily returns.
    """
    stock_data = get_all_stocks_df(db, 365)

    if len(stock_data) < 2:
        raise HTTPException(
            status_code=503,
            detail="Insufficient data to generate correlation matrix"
        )

    matrix_data = generate_correlation_matrix(stock_data)

    if 'error' in matrix_data:
        raise HTTPException(
            status_code=400,
            detail=matrix_data['error']
        )

    return CorrelationMatrixResponse(**matrix_data)
