"""
Companies API router.

Provides endpoints for listing and retrieving company information.

Endpoint: GET /companies
- Returns list of all available companies with current prices
"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.company import CompanyInfo, CompanyListResponse
from app.services.data_fetcher import fetch_latest_price
from app.services.cache_service import (
    companies_cache, 
    get_cached, 
    set_cached
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=CompanyListResponse)
async def get_companies():
    """
    Get list of all available companies.
    
    Returns company symbols, names, current prices, and daily changes.
    Results are cached for 5 minutes.
    """
    cache_key = "all_companies"
    
    # Check cache
    cached = get_cached(companies_cache, cache_key)
    if cached:
        return cached
    
    companies = []
    
    for symbol in STOCK_SYMBOLS:
        company_info = {
            'symbol': symbol,
            'name': COMPANY_NAMES.get(symbol, symbol.replace('.NS', '')),
            'current_price': None,
            'daily_change': None
        }
        
        # Fetch latest price
        price_data = fetch_latest_price(symbol)
        if price_data:
            company_info['current_price'] = price_data['current_price']
            company_info['daily_change'] = price_data['daily_change']
        
        companies.append(CompanyInfo(**company_info))
    
    response = CompanyListResponse(
        count=len(companies),
        companies=companies
    )
    
    # Cache response
    set_cached(companies_cache, cache_key, response)
    
    return response


@router.get("/{symbol}", response_model=CompanyInfo)
async def get_company(symbol: str):
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
    
    company_info = {
        'symbol': symbol,
        'name': COMPANY_NAMES.get(symbol, symbol.replace('.NS', '')),
        'current_price': None,
        'daily_change': None
    }
    
    price_data = fetch_latest_price(symbol)
    if price_data:
        company_info['current_price'] = price_data['current_price']
        company_info['daily_change'] = price_data['daily_change']
    
    return CompanyInfo(**company_info)
