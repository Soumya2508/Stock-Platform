"""
Metrics calculation service for stock data.

This module calculates all financial metrics:
- Daily Return
- Moving Averages (7-day, 20-day)
- 52-week High/Low
- Volatility Score
- Momentum Index
- Trend Strength

Challenges:
- Handling edge cases at the start of data series
- Normalizing volatility scores across different price ranges
- Ensuring calculations are numerically stable

Future Improvements:
- Add more technical indicators (RSI, MACD, Bollinger Bands)
- Implement sector-relative metrics
- Add custom metric configuration
"""

import pandas as pd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def calculate_daily_return(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily return percentage.
    
    Formula: (Close - Open) / Open * 100
    
    Args:
        df: DataFrame with 'open' and 'close' columns
    
    Returns:
        DataFrame with 'daily_return' column added
    """
    if 'open' in df.columns and 'close' in df.columns:
        df['daily_return'] = ((df['close'] - df['open']) / df['open'] * 100).round(2)
    return df


def calculate_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate moving averages.
    
    Calculates:
    - 7-day moving average (short-term trend)
    - 20-day moving average (medium-term trend)
    
    Args:
        df: DataFrame with 'close' column
    
    Returns:
        DataFrame with 'ma_7' and 'ma_20' columns added
    """
    if 'close' in df.columns:
        df['ma_7'] = df['close'].rolling(window=7, min_periods=1).mean().round(2)
        df['ma_20'] = df['close'].rolling(window=20, min_periods=1).mean().round(2)
    return df


def calculate_52_week_high_low(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 52-week (252 trading days) high and low.
    
    Uses rolling window to calculate trailing 52-week highs and lows.
    The high is the maximum of open, high, close columns.
    The low is the minimum of open, low, close columns.
    
    Args:
        df: DataFrame with 'high', 'low', 'open', 'close' columns
    
    Returns:
        DataFrame with 'high_52w' and 'low_52w' columns added
    """
    trading_days_per_year = 252
    
    # Calculate the max price for each day (considering open, high, close)
    if all(col in df.columns for col in ['open', 'high', 'close']):
        daily_max = df[['open', 'high', 'close']].max(axis=1)
        df['high_52w'] = daily_max.rolling(
            window=trading_days_per_year, 
            min_periods=1
        ).max().round(2)
    elif 'high' in df.columns:
        df['high_52w'] = df['high'].rolling(
            window=trading_days_per_year, 
            min_periods=1
        ).max().round(2)
    
    # Calculate the min price for each day (considering open, low, close)
    if all(col in df.columns for col in ['open', 'low', 'close']):
        daily_min = df[['open', 'low', 'close']].min(axis=1)
        df['low_52w'] = daily_min.rolling(
            window=trading_days_per_year, 
            min_periods=1
        ).min().round(2)
    elif 'low' in df.columns:
        df['low_52w'] = df['low'].rolling(
            window=trading_days_per_year, 
            min_periods=1
        ).min().round(2)
    
    return df


def calculate_volatility(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Calculate volatility score based on standard deviation of daily returns.
    
    The score is normalized to 0-100 scale where:
    - 0-20: Low volatility
    - 20-50: Moderate volatility
    - 50-100: High volatility
    
    Args:
        df: DataFrame with 'daily_return' column
        window: Rolling window size (default 30 days)
    
    Returns:
        DataFrame with 'volatility' column added
    """
    if 'daily_return' not in df.columns:
        df = calculate_daily_return(df)
    
    # Calculate rolling standard deviation
    rolling_std = df['daily_return'].rolling(window=window, min_periods=5).std()
    
    # Normalize to 0-100 scale (typical daily stock volatility is 0-5%)
    # Using 5% as the max expected daily volatility for normalization
    max_volatility = 5.0
    df['volatility'] = (rolling_std / max_volatility * 100).clip(0, 100).round(2)
    
    return df


def calculate_momentum(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Calculate momentum index (rate of change).
    
    Formula: (Current Price - Price N days ago) / Price N days ago * 100
    
    Interpretation:
    - Positive: Upward momentum
    - Negative: Downward momentum
    - Magnitude indicates strength
    
    Args:
        df: DataFrame with 'close' column
        window: Lookback period (default 20 days)
    
    Returns:
        DataFrame with 'momentum' column added
    """
    if 'close' in df.columns:
        df['momentum'] = df['close'].pct_change(periods=window).mul(100).round(2)
    return df


def calculate_trend_strength(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate trend strength based on price vs moving average.
    
    Measures how consistently the price stays above/below the 20-day MA.
    
    Score interpretation:
    - Positive: Bullish trend
    - Negative: Bearish trend
    - Magnitude: Trend strength
    
    Args:
        df: DataFrame with 'close' and 'ma_20' columns
    
    Returns:
        DataFrame with 'trend_strength' column added
    """
    if 'close' in df.columns and 'ma_20' in df.columns:
        # Calculate percentage above/below MA
        df['trend_strength'] = ((df['close'] - df['ma_20']) / df['ma_20'] * 100).round(2)
    return df


def calculate_all_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all metrics for the stock data.
    
    This is the main function that applies all metric calculations
    in the correct order.
    
    Args:
        df: Raw or cleaned DataFrame
    
    Returns:
        DataFrame with all metrics calculated
    """
    if df.empty:
        return df
    
    logger.info(f"Calculating metrics for {len(df)} records")
    
    # Apply calculations in order (some depend on others)
    df = calculate_daily_return(df)
    df = calculate_moving_averages(df)
    df = calculate_52_week_high_low(df)
    df = calculate_volatility(df)
    df = calculate_momentum(df)
    df = calculate_trend_strength(df)
    
    # Fill any NaN values at the start of series with appropriate defaults
    df['volatility'] = df['volatility'].fillna(0)
    df['momentum'] = df['momentum'].fillna(0)
    df['trend_strength'] = df['trend_strength'].fillna(0)
    
    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Get summary statistics for a stock.
    
    Args:
        df: DataFrame with all metrics calculated
    
    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    
    return {
        'current_price': float(latest['close']),
        'daily_return': float(latest['daily_return']) if 'daily_return' in df.columns else 0,
        'high_52w': float(df['high_52w'].max()) if 'high_52w' in df.columns else 0,
        'low_52w': float(df['low_52w'].min()) if 'low_52w' in df.columns else 0,
        'avg_close': float(df['close'].mean()),
        'volatility': float(latest['volatility']) if 'volatility' in df.columns else 0,
        'momentum': float(latest['momentum']) if 'momentum' in df.columns else 0,
        'trend_strength': float(latest['trend_strength']) if 'trend_strength' in df.columns else 0,
        'avg_volume': int(df['volume'].mean()),
    }
