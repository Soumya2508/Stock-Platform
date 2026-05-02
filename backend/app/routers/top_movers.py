"""
Top Movers API router.

Provides endpoint for top gaining and losing stocks.

Endpoint: GET /top-movers
- Returns top 5 gainers and top 5 losers
- All data served from SQLite
"""

from fastapi import APIRouter, Depends
from datetime import date
import logging
from sqlalchemy.orm import Session

from app.config import STOCK_SYMBOLS, COMPANY_NAMES
from app.schemas.stock_data import TopMoversResponse, TopMover
from app.database.connection import get_db
from app.services.data_fetcher import get_latest_prices_bulk

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/top-movers", tags=["Top Movers"])


@router.get("", response_model=TopMoversResponse)
async def get_top_movers(db: Session = Depends(get_db)):
    """
    Get top gainers and losers of the day.

    Returns:
    - Top 5 stocks with highest daily gains
    - Top 5 stocks with highest daily losses
    """
    all_stocks = []

    prices_map = get_latest_prices_bulk(db, STOCK_SYMBOLS)

    for symbol in STOCK_SYMBOLS:
        if symbol in prices_map:
            price_data = prices_map[symbol]
            all_stocks.append({
                'symbol': symbol,
                'name': COMPANY_NAMES.get(symbol, symbol.replace('.NS', '')),
                'current_price': price_data['current_price'],
                'daily_change': price_data['daily_change']
            })

    # Sort by daily change
    sorted_stocks = sorted(all_stocks, key=lambda x: x['daily_change'], reverse=True)

    # Get top 5 gainers and losers
    gainers = [TopMover(**s) for s in sorted_stocks[:5] if s['daily_change'] > 0]
    losers = [TopMover(**s) for s in sorted_stocks[-5:][::-1] if s['daily_change'] < 0]

    return TopMoversResponse(
        date=str(date.today()),
        gainers=gainers,
        losers=losers,
    )
