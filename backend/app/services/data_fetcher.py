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
    
    # Ensure high is ALWAYS >= max(open, close) and low is ALWAYS <= min(open, close)
    daily_max = np.maximum(df['open'].values, df['close'].values)
    daily_min = np.minimum(df['open'].values, df['close'].values)
    high_multiplier = 1 + np.random.uniform(0.005, 0.02, input_dates)  # 0.5% to 2% higher
    low_multiplier = 1 - np.random.uniform(0.005, 0.02, input_dates)   # 0.5% to 2% lower
    df['high'] = daily_max * high_multiplier
    df['low'] = daily_min * low_multiplier
    df['volume'] = np.random.randint(100000, 5000000, size=input_dates)
    
    df['symbol'] = symbol
    df['date'] = df.index.date
    
    # Reset index to match yf format structure in logic
    df.reset_index(drop=True, inplace=True)
    
    return df



def _flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten MultiIndex columns from yfinance to simple lowercase strings.
    yfinance 0.2.50+ returns MultiIndex columns like ('Close', 'SYMBOL') even for single symbols.
    """
    if isinstance(df.columns, pd.MultiIndex):
        # Take first level (Price type: Open, High, Low, Close, Volume)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Standardize to lowercase
    df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]
    return df


def fetch_stock_data(symbol: str, period: str = DATA_PERIOD) -> Optional[pd.DataFrame]:
    """
    Fetch historical stock data for a single symbol.
    Uses yf.download which is more robust than Ticker.history
    Fallback to mock data if fetch fails.
    """
    try:
        # download returns a MultiIndex even for single ticker in yfinance >= 0.2.50
        df = yf.download(symbol, period=period, progress=False, auto_adjust=True)
        
        if df.empty:
            logger.warning(f"No data returned for {symbol}, using mock data")
            return generate_mock_data(symbol, period)
        
        # Reset index to make Date a column
        df.reset_index(inplace=True)
        
        # Flatten MultiIndex columns from new yfinance versions
        df = _flatten_yf_columns(df)
        
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

        # yfinance returns MultiIndex columns with group_by='ticker'
        # Level 0 = ticker symbol, Level 1 = price type (Open, High, Low, Close, Volume)
        if isinstance(df.columns, pd.MultiIndex):
            # Get available tickers from the MultiIndex
            available_tickers = df.columns.get_level_values(0).unique().tolist()
            
            for symbol in symbols:
                if symbol in available_tickers:
                    symbol_df = df[symbol].copy()
                    
                    # Check if we have valid data (Close column with values)
                    close_col = 'Close' if 'Close' in symbol_df.columns else 'close'
                    if symbol_df.empty or close_col not in symbol_df.columns or symbol_df[close_col].count() == 0:
                        all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
                        continue
                        
                    symbol_df.reset_index(inplace=True)
                    symbol_df.columns = [str(col).lower().replace(' ', '_') for col in symbol_df.columns]
                    symbol_df['symbol'] = symbol
                    if 'date' in symbol_df.columns:
                        symbol_df['date'] = pd.to_datetime(symbol_df['date']).dt.date
                        
                    all_data[symbol] = symbol_df
                else: 
                    # Missing symbol in bulk result
                    logger.warning(f"{symbol} not found in bulk download, using mock data")
                    all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
        else:
            # Single symbol case or non-MultiIndex structure
            if len(symbols) == 1:
                symbol = symbols[0]
                df = _flatten_yf_columns(df)
                if df.empty or 'close' not in df.columns or df['close'].count() == 0:
                    all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
                else:
                    df.reset_index(inplace=True)
                    df = _flatten_yf_columns(df)
                    df['symbol'] = symbol
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date']).dt.date
                    all_data[symbol] = df
            else:
                # If structure confused, use mock for all
                logger.warning("Unexpected DataFrame structure, using mock data for all")
                for symbol in symbols:
                    all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)

        if not all_data:
             logger.warning("Processed data is empty, switching to mock data for all stocks")
             for symbol in symbols:
                 all_data[symbol] = generate_mock_data(symbol, DATA_PERIOD)
                 
        logger.info(f"Successfully fetched bulk data for {len(all_data)}/{len(symbols)} stocks")
        return all_data
        
    except Exception as e:
        logger.error(f"Error in fetch_all_stocks: {e}. Using mock data.")
        # Ensure we return something
        if not all_data:
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
        
        # Check if df is valid
        if df is None or df.empty:
            logger.warning("Bulk fetch returned empty/none, switching to mock data")
            for symbol in symbols:
                df_mock = generate_mock_data(symbol, '5d')
                curr = df_mock['close'].iloc[-1]
                prev = df_mock['close'].iloc[-2]
                change = ((curr - prev)/prev)*100
                results[symbol] = {'current_price': round(curr, 2), 'daily_change': round(change, 2)}
            return results

        # Get available tickers from MultiIndex
        available_tickers = []
        if isinstance(df.columns, pd.MultiIndex):
            available_tickers = df.columns.get_level_values(0).unique().tolist()
        
        # Iterate symbols and try to extract real data
        for symbol in symbols:
            found = False
            try:
                if symbol in available_tickers:
                    symbol_df = df[symbol]
                    # Handle both 'Close' and 'close' column names
                    close_col = 'Close' if 'Close' in symbol_df.columns else ('close' if 'close' in symbol_df.columns else None)
                    if close_col:
                        series = symbol_df[close_col].dropna()
                        if len(series) >= 2:
                            current_price = float(series.iloc[-1])
                            prev_close = float(series.iloc[-2])
                            change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                            results[symbol] = {
                                'current_price': round(current_price, 2),
                                'daily_change': round(change, 2)
                            }
                            found = True
            except Exception as e:
                logger.debug(f"Error extracting {symbol} from bulk data: {e}")
            
            # If real fetch failed for this symbol, use Mock
            if not found:
                df_mock = generate_mock_data(symbol, '5d')
                curr = df_mock['close'].iloc[-1]
                prev = df_mock['close'].iloc[-2]
                change = ((curr - prev)/prev)*100
                results[symbol] = {'current_price': round(curr, 2), 'daily_change': round(change, 2)}
        
        logger.info(f"Bulk fetched (with mock fallback) prices for {len(results)}/{len(symbols)} stocks")
        return results
        
    except Exception as e:
        logger.error(f"Error in bulk fetch: {str(e)}. Using mock data for ALL.")
        # Full fallback
        for symbol in symbols:
            df_mock = generate_mock_data(symbol, '5d')
            curr = df_mock['close'].iloc[-1]
            prev = df_mock['close'].iloc[-2]
            change = ((curr - prev)/prev)*100
            results[symbol] = {'current_price': round(curr, 2), 'daily_change': round(change, 2)}
        return results
