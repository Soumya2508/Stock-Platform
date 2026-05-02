"""
Companies API router.

Provides endpoints for listing and retrieving company information.

Endpoint: GET /companies
- Returns list of all available companies with current prices
- All data served from SQLite (seeded from static JSON)
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from sqlalchemy.orm import Session

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.company import CompanyInfo, CompanyListResponse
from app.database.connection import get_db
from app.services.data_fetcher import get_latest_prices_bulk, get_latest_price

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=CompanyListResponse)
async def get_companies(db: Session = Depends(get_db)):
    """
    Get list of all available companies.

    Returns company symbols, names, current prices, and daily changes.
    """
    companies = []

    prices_map = get_latest_prices_bulk(db, STOCK_SYMBOLS)

    for symbol in STOCK_SYMBOLS:
        company_info = {
            'symbol': symbol,
            'name': COMPANY_NAMES.get(symbol, symbol.replace('.NS', '')),
            'current_price': None,
            'daily_change': None
        }

        if symbol in prices_map:
            company_info['current_price'] = prices_map[symbol]['current_price']
            company_info['daily_change'] = prices_map[symbol]['daily_change']

        companies.append(CompanyInfo(**company_info))

    return CompanyListResponse(
        count=len(companies),
        companies=companies
    )


@router.get("/{symbol}", response_model=CompanyInfo)
async def get_company(symbol: str, db: Session = Depends(get_db)):
    """
    Get information for a specific company.

    Args:
        symbol: Stock ticker symbol (e.g., TCS.NS)
    """
    # Normalize symbol
    if not symbol.endswith('.NS'):
        symbol = f"{symbol}.NS"

    if symbol not in STOCK_SYMBOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Company {symbol} not found"
        )

    price_data = get_latest_price(db, symbol)

    return CompanyInfo(
        symbol=symbol,
        name=COMPANY_NAMES.get(symbol, symbol.replace('.NS', '')),
        current_price=price_data['current_price'],
        daily_change=price_data['daily_change'],
    )
