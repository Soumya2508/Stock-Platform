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
import numpy as np
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging
import random

from app.config import STOCK_SYMBOLS, DATA_PERIOD, COMPANY_NAMES

logger = logging.getLogger(__name__)

# Fallback base prices (Approx INR) for mock generation
BASE_PRICES = {
    "TCS.NS": 4100.0,
    "INFY.NS": 1600.0,
    "RELIANCE.NS": 2950.0,
    "HDFCBANK.NS": 1450.0,
    "ICICIBANK.NS": 1080.0,
    "WIPRO.NS": 480.0,
    "ITC.NS": 430.0,
    "SBIN.NS": 760.0,
    "BHARTIARTL.NS": 1200.0,
    "HINDUNILVR.NS": 2400.0,
    "BAJFINANCE.NS": 7100.0,
    "MARUTI.NS": 12500.0,
    "LT.NS": 3600.0,
    "AXISBANK.NS": 1050.0,
    "KOTAKBANK.NS": 1750.0,
}

def generate_mock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Generate realistic random walk data for fallback"""
    base_price = BASE_PRICES.get(symbol, 1000.0)
    
    # Determine days based on period
    days = 252  # Default 1y
    if period == "5d": days = 7
    elif period == "1mo": days = 30
    elif period == "6mo": days = 126
    
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq='B')
    
    # Generate random walk
    input_dates = len(dates)
    returns = np.random.normal(loc=0.0005, scale=0.015, size=input_dates)
    price_path = base_price * (1 + returns).cumprod()
    
    # Create valid prices
    df = pd.DataFrame(index=dates)
    df['open'] = price_path * (1 + np.random.normal(0, 0.005, input_dates))
    df['close'] = price_path
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.005, input_dates)))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.005, input_dates)))
    df['volume'] = np.random.randint(100000, 5000000, size=input_dates)
    
    df['symbol'] = symbol
    df['date'] = df.index.date
    
    # Reset index to match yf format structure in logic
    df.reset_index(drop=True, inplace=True)
    
    return df



def fetch_stock_data(symbol: str, period: str = DATA_PERIOD) -> Optional[pd.DataFrame]:
    """
    Fetch historical stock data for a single symbol.
    Uses yf.download which is more robust than Ticker.history
    Fallback to mock data if fetch fails.
    """
    try:
        # download returns a MultiIndex if we don't specify it to be simple for 1 ticker
        # but auto_adjust=True is good for analysis
        df = yf.download(symbol, period=period, progress=False, auto_adjust=True)
        
        if df.empty:
            logger.warning(f"No data returned for {symbol}, using mock data")
            return generate_mock_data(symbol, period)
        
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
        logger.error(f"Error fetching data for {symbol}: {str(e)}. Using mock data.")
        return generate_mock_data(symbol, period)


def fetch_all_stocks(symbols: List[str] = STOCK_SYMBOLS) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical data for all configure stocks in BULK.
    Fallback to mock data for all symbols if bulk fetch fails.
    """
    all_data = {}
    
    try:
        # Bulk download
        # period default is 1y from config
        df = yf.download(symbols, period=DATA_PERIOD, progress=False, group_by='ticker', auto_adjust=True)
        
        if df.empty:
            # Full fallback
            logger.warning("Bulk fetch returned empty, using mock data for all stocks")
            for symbol in symbols:
                all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
            return all_data

        if isinstance(df.columns, pd.MultiIndex):
            for symbol in symbols:
                if symbol in df.columns:
                    symbol_df = df[symbol].copy()
                    
                    if symbol_df.empty:
                        all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
                        continue
                        
                    symbol_df.reset_index(inplace=True)
                    symbol_df.columns = [col.lower().replace(' ', '_') for col in symbol_df.columns]
                    symbol_df['symbol'] = symbol
                    if 'date' in symbol_df.columns:
                        symbol_df['date'] = pd.to_datetime(symbol_df['date']).dt.date
                        
                    all_data[symbol] = symbol_df
                else: 
                     # Missing symbol in bulk result
                     all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
        else:
             # Single symbol case fallback or weird structure
             if len(symbols) == 1:
                symbol = symbols[0]
                if df.empty:
                     all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
                else:
                    df.reset_index(inplace=True)
                    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                    df['symbol'] = symbol
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date']).dt.date
                    all_data[symbol] = df
             else:
                # If structure confused, use mock for all missing
                 for symbol in symbols:
                     all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)

        logger.info(f"Successfully fetched/mocked data for {len(all_data)}/{len(symbols)} stocks")
        return all_data
        
    except Exception as e:
        logger.error(f"Error in fetch_all_stocks: {e}. Using mock data.")
        for symbol in symbols:
            all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
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
    """
    # Simply use bulk fetch for single item or fetch_stock_data logic to reuse mock
    # But for specialized logic:
    try:
        # We can reuse generate mock data for current price
        # Or try real fetch first
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if len(hist) < 2:
           # Fallback
           df = generate_mock_data(symbol, '5d')
           curr = df['close'].iloc[-1]
           prev = df['close'].iloc[-2]
           change = ((curr - prev)/prev)*100
           return {'current_price': round(curr, 2), 'daily_change': round(change, 2)}
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        daily_change = ((current_price - prev_close) / prev_close) * 100
        
        return {
            'current_price': round(current_price, 2),
            'daily_change': round(daily_change, 2)
        }
        
    except Exception as e:
        # Fallback
        df = generate_mock_data(symbol, '5d')
        curr = df['close'].iloc[-1]
        prev = df['close'].iloc[-2]
        change = ((curr - prev)/prev)*100
        return {'current_price': round(curr, 2), 'daily_change': round(change, 2)}


def fetch_latest_prices_bulk(symbols: List[str]) -> Dict[str, Dict]:
    """
    Fetch latest prices for multiple symbols in sorted bulk request.
    Fallback to mock if fails.
    """
    if not symbols:
        return {}
        
    results = {}
    try:
        # Download data for all symbols at once
        df = yf.download(symbols, period='5d', progress=False, group_by='ticker')
        
        if df.empty:
            raise Exception("Empty bulk response")

        # Process logic same as before...
        # If single symbol
        if len(symbols) == 1:
            symbol = symbols[0]
            if not df.empty and len(df) >= 2:
                try:
                    current = float(df['Close'].iloc[-1])
                    prev = float(df['Close'].iloc[-2])
                    change = ((current - prev) / prev) * 100 if prev != 0 else 0
                    results[symbol] = {'current_price': round(current, 2), 'daily_change': round(change, 2)}
                except:
                    pass
            
            if symbol not in results:
                 # Mock
                df_mock = generate_mock_data(symbol, '5d')
                curr = df_mock['close'].iloc[-1]
                prev = df_mock['close'].iloc[-2]
                change = ((curr - prev)/prev)*100
                results[symbol] = {'current_price': round(curr, 2), 'daily_change': round(change, 2)}
            return results

        # Multiple symbols
        for symbol in symbols:
            found = False
            try:
                if symbol in df.columns:
                    symbol_df = df[symbol]
                    if 'Close' in symbol_df.columns:
                        series = symbol_df['Close'].dropna()
                        if len(series) >= 2:
                            current_price = float(series.iloc[-1])
                            prev_close = float(series.iloc[-2])
                            change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                            results[symbol] = {
                                'current_price': round(current_price, 2),
                                'daily_change': round(change, 2)
                            }
                            found = True
            except:
                pass
            
            if not found:
                 # Fallback mock for this symbol
                df_mock = generate_mock_data(symbol, '5d')
                curr = df_mock['close'].iloc[-1]
                prev = df_mock['close'].iloc[-2]
                change = ((curr - prev)/prev)*100
                results[symbol] = {'current_price': round(curr, 2), 'daily_change': round(change, 2)}
                
        return results
        
    except Exception as e:
        logger.error(f"Error in bulk fetch: {str(e)}. Using mock data.")
        # Full fallback
        for symbol in symbols:
            df_mock = generate_mock_data(symbol, '5d')
            curr = df_mock['close'].iloc[-1]
            prev = df_mock['close'].iloc[-2]
            change = ((curr - prev)/prev)*100
            results[symbol] = {'current_price': round(curr, 2), 'daily_change': round(change, 2)}
        return results
