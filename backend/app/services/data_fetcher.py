"""
Stock data fetching service using yfinance.

This module handles:
- Fetching historical stock data from Yahoo Finance
- Downloading data for multiple symbols
- Error handling for API failures

Challenges:
- yfinance rate limiting during bulk downloads
- Handling network timeouts and API errors
- Data availability gaps for some stocks

Future Improvements:
- Add retry logic with exponential backoff
- Implement parallel fetching for faster downloads
- Cache raw data to reduce API calls
"""

import yfinance as yf
import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from app.config import STOCK_SYMBOLS, DATA_PERIOD, COMPANY_NAMES

logger = logging.getLogger(__name__)


def fetch_stock_data(symbol: str, period: str = DATA_PERIOD) -> Optional[pd.DataFrame]:
    """
    Fetch historical stock data for a single symbol.
    
    Args:
        symbol: Stock ticker (e.g., 'TCS.NS')
        period: Data period ('1y', '6mo', '3mo', etc.)
    
    Returns:
        DataFrame with OHLCV data or None if fetch fails
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            logger.warning(f"No data returned for {symbol}")
            return None
        
        # Reset index to make Date a column
        df.reset_index(inplace=True)
        
        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Add symbol column
        df['symbol'] = symbol
        
        # Convert date to date only (remove time)
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        logger.info(f"Fetched {len(df)} records for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None


def fetch_all_stocks(symbols: List[str] = STOCK_SYMBOLS) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical data for all configured stock symbols.
    
    Args:
        symbols: List of stock tickers to fetch
    
    Returns:
        Dictionary mapping symbol to DataFrame
    """
    all_data = {}
    
    for symbol in symbols:
        df = fetch_stock_data(symbol)
        if df is not None:
            all_data[symbol] = df
    
    logger.info(f"Successfully fetched data for {len(all_data)}/{len(symbols)} stocks")
    return all_data


def get_company_info(symbol: str) -> Dict:
    """
    Get company information for a stock symbol.
    
    Args:
        symbol: Stock ticker
    
    Returns:
        Dictionary with company name and info
    """
    return {
        'symbol': symbol,
        'name': COMPANY_NAMES.get(symbol, symbol.replace('.NS', '')),
    }


def fetch_latest_price(symbol: str) -> Optional[Dict]:
    """
    Fetch the latest price data for a symbol.
    
    Args:
        symbol: Stock ticker
    
    Returns:
        Dictionary with current price and daily change
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if len(hist) < 2:
            return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        daily_change = ((current_price - prev_close) / prev_close) * 100
        
        return {
            'current_price': round(current_price, 2),
            'daily_change': round(daily_change, 2)
        }
        
    except Exception as e:
        logger.error(f"Error fetching latest price for {symbol}: {str(e)}")
        return None
