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
    Uses yf.download which is more robust than Ticker.history
    """
    try:
        # download returns a MultiIndex if we don't specify it to be simple for 1 ticker
        # but auto_adjust=True is good for analysis
        df = yf.download(symbol, period=period, progress=False, auto_adjust=True)
        
        if df.empty:
            logger.warning(f"No data returned for {symbol}")
            return None
        
        # Reset index to make Date a column
        df.reset_index(inplace=True)
        
        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Add symbol column
        df['symbol'] = symbol
        
        # Convert date to date only
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
        
        logger.info(f"Fetched {len(df)} records for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None


def fetch_all_stocks(symbols: List[str] = STOCK_SYMBOLS) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical data for all configure stocks in BULK.
    """
    all_data = {}
    
    try:
        # Bulk download
        # period default is 1y from config
        df = yf.download(symbols, period=DATA_PERIOD, progress=False, group_by='ticker', auto_adjust=True)
        
        if df.empty:
            return {}

        if isinstance(df.columns, pd.MultiIndex):
            for symbol in symbols:
                if symbol in df.columns:
                    symbol_df = df[symbol].copy()
                    
                    if symbol_df.empty:
                        continue
                        
                    symbol_df.reset_index(inplace=True)
                    symbol_df.columns = [col.lower().replace(' ', '_') for col in symbol_df.columns]
                    symbol_df['symbol'] = symbol
                    if 'date' in symbol_df.columns:
                        symbol_df['date'] = pd.to_datetime(symbol_df['date']).dt.date
                        
                    all_data[symbol] = symbol_df
        else:
             # Single symbol case fallback
             if len(symbols) == 1:
                symbol = symbols[0]
                df.reset_index(inplace=True)
                df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                df['symbol'] = symbol
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date']).dt.date
                all_data[symbol] = df

        logger.info(f"Successfully fetched bulk data for {len(all_data)}/{len(symbols)} stocks")
        return all_data
        
    except Exception as e:
        logger.error(f"Error in fetch_all_stocks: {e}")
        return {}


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


def fetch_latest_prices_bulk(symbols: List[str]) -> Dict[str, Dict]:
    """
    Fetch latest prices for multiple symbols in a single request.
    Much faster than calling fetch_latest_price sequentially.
    
    Args:
        symbols: List of stock tickers
        
    Returns:
        Dictionary mapping symbol to {current_price, daily_change}
    """
    if not symbols:
        return {}
        
    try:
        # Download data for all symbols at once
        # Using period='5d' to ensure we have enough data for change calculation
        # group_by='ticker' ensures simpler column structure
        df = yf.download(symbols, period='5d', progress=False, group_by='ticker')
        
        results = {}
        
        # If only one symbol, yf doesn't return multi-index with ticker at top level
        if len(symbols) == 1:
            symbol = symbols[0]
            if not df.empty and len(df) >= 2:
                try:
                    current = float(df['Close'].iloc[-1])
                    prev = float(df['Close'].iloc[-2])
                    change = ((current - prev) / prev) * 100 if prev != 0 else 0
                    results[symbol] = {'current_price': round(current, 2), 'daily_change': round(change, 2)}
                except Exception as e:
                    logger.error(f"Error parse single symbol {symbol}: {e}")
            return results

        # Multiple symbols
        for symbol in symbols:
            try:
                # Check if symbol is in columns (top level)
                if symbol in df.columns:
                    symbol_df = df[symbol]
                    # Ensure we have Close column
                    if 'Close' in symbol_df.columns:
                        series = symbol_df['Close'].dropna()
                        
                        if len(series) >= 2:
                            current_price = float(series.iloc[-1])
                            prev_close = float(series.iloc[-2])
                            
                            # Handle zero division
                            if prev_close == 0:
                                change = 0.0
                            else:
                                change = ((current_price - prev_close) / prev_close) * 100
                                
                            results[symbol] = {
                                'current_price': round(current_price, 2),
                                'daily_change': round(change, 2)
                            }
            except Exception as e:
                logger.warning(f"Error processing {symbol} in bulk fetch: {e}")
                continue
                
        logger.info(f"Bulk fetched prices for {len(results)}/{len(symbols)} stocks")
        return results
        
    except Exception as e:
        logger.error(f"Error in bulk fetch: {str(e)}")
        return {}
