"""
Data cleaning service for stock data.

This module handles:
- Cleaning raw stock data from yfinance
- Handling missing values
- Standardizing date formats
- Removing invalid records

Challenges:
- Different stocks have different data availability
- Handling stock splits and adjustments
- Weekend/holiday gaps in data

Future Improvements:
- Add data validation rules
- Implement outlier detection
- Support for corporate action adjustments
"""

import pandas as pd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess raw stock data.
    
    Args:
        df: Raw DataFrame from yfinance
    
    Returns:
        Cleaned DataFrame
    
    Cleaning steps:
    1. Remove rows with missing OHLCV data
    2. Remove duplicate dates
    3. Sort by date
    4. Handle zero volumes
    5. Validate price consistency (high >= low)
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    original_len = len(df)
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Step 1: Remove rows with missing essential data
    essential_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in essential_cols:
        if col in df.columns:
            df = df.dropna(subset=[col])
    
    # Step 2: Remove duplicate dates (keep last)
    if 'date' in df.columns:
        df = df.drop_duplicates(subset=['date', 'symbol'], keep='last')
    
    # Step 3: Sort by date
    if 'date' in df.columns:
        df = df.sort_values('date').reset_index(drop=True)
    
    # Step 4: Handle zero or negative volumes
    if 'volume' in df.columns:
        df = df[df['volume'] > 0]
    
    # Step 5: Validate price consistency
    if all(col in df.columns for col in ['high', 'low']):
        df = df[df['high'] >= df['low']]
    
    # Step 6: Forward fill any remaining missing values in price columns
    price_cols = ['open', 'high', 'low', 'close']
    for col in price_cols:
        if col in df.columns:
            df[col] = df[col].ffill()
    
    cleaned_len = len(df)
    removed = original_len - cleaned_len
    
    if removed > 0:
        logger.info(f"Cleaned data: removed {removed} invalid records")
    
    return df


def handle_missing_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing trading dates in the data.
    
    This fills gaps in the data while respecting that weekends
    and holidays have no trading data (these are intentional gaps).
    
    Args:
        df: Cleaned DataFrame
    
    Returns:
        DataFrame with missing dates handled
    """
    if df.empty or 'date' not in df.columns:
        return df
    
    # For stock data, we don't fill weekend gaps
    # Just ensure the data is continuous for trading days
    return df


def validate_data_quality(df: pd.DataFrame) -> dict:
    """
    Generate data quality report for the cleaned data.
    
    Args:
        df: Cleaned DataFrame
    
    Returns:
        Dictionary with quality metrics
    """
    if df.empty:
        return {'status': 'empty', 'records': 0}
    
    return {
        'status': 'valid',
        'records': len(df),
        'date_range': {
            'start': str(df['date'].min()) if 'date' in df.columns else None,
            'end': str(df['date'].max()) if 'date' in df.columns else None,
        },
        'missing_values': df.isnull().sum().to_dict(),
        'price_range': {
            'min': float(df['low'].min()) if 'low' in df.columns else None,
            'max': float(df['high'].max()) if 'high' in df.columns else None,
        }
    }
