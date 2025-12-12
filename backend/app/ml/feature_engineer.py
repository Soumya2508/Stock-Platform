"""
Feature engineering for ML model.

This module prepares features for the XGBoost prediction model:
- Technical indicators as features
- Lag features
- Time-based features

Challenges:
- Feature selection for optimal prediction
- Handling look-ahead bias in features
- Feature scaling considerations

Future Improvements:
- Add more technical indicators
- Implement feature importance analysis
- Add automated feature selection
"""

import pandas as pd
import numpy as np
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


def create_lag_features(df: pd.DataFrame, column: str, lags: List[int]) -> pd.DataFrame:
    """
    Create lag features for a given column.
    
    Args:
        df: Input DataFrame
        column: Column to create lags for
        lags: List of lag periods
    
    Returns:
        DataFrame with lag features added
    """
    for lag in lags:
        df[f'{column}_lag_{lag}'] = df[column].shift(lag)
    return df


def create_rolling_features(df: pd.DataFrame, column: str, windows: List[int]) -> pd.DataFrame:
    """
    Create rolling window features.
    
    Args:
        df: Input DataFrame
        column: Column to calculate rolling features for
        windows: List of window sizes
    
    Returns:
        DataFrame with rolling features added
    """
    for window in windows:
        df[f'{column}_roll_mean_{window}'] = df[column].rolling(window=window).mean()
        df[f'{column}_roll_std_{window}'] = df[column].rolling(window=window).std()
        df[f'{column}_roll_min_{window}'] = df[column].rolling(window=window).min()
        df[f'{column}_roll_max_{window}'] = df[column].rolling(window=window).max()
    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based features.
    
    Args:
        df: DataFrame with 'date' column
    
    Returns:
        DataFrame with time features added
    """
    if 'date' not in df.columns:
        return df
    
    df['date_temp'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date_temp'].dt.dayofweek
    df['day_of_month'] = df['date_temp'].dt.day
    df['month'] = df['date_temp'].dt.month
    df['week_of_year'] = df['date_temp'].dt.isocalendar().week.astype(int)
    df = df.drop(columns=['date_temp'])
    
    return df


def create_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create price-based features.
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        DataFrame with price features added
    """
    # Price range features
    df['price_range'] = df['high'] - df['low']
    df['price_range_pct'] = (df['high'] - df['low']) / df['close'] * 100
    
    # Gap features (today's open vs yesterday's close)
    df['gap'] = df['open'] - df['close'].shift(1)
    df['gap_pct'] = df['gap'] / df['close'].shift(1) * 100
    
    # Close position within range
    df['close_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
    df['close_position'] = df['close_position'].fillna(0.5)
    
    return df


def create_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create volume-based features.
    
    Args:
        df: DataFrame with volume data
    
    Returns:
        DataFrame with volume features added
    """
    if 'volume' not in df.columns:
        return df
    
    # Volume change
    df['volume_change'] = df['volume'].pct_change()
    
    # Volume relative to moving average
    df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma_5']
    df['volume_ratio'] = df['volume_ratio'].fillna(1)
    
    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main function to prepare all features for ML model.
    
    Args:
        df: Raw DataFrame with stock data
    
    Returns:
        DataFrame with all features
    """
    if df.empty:
        return df
    
    logger.info(f"Preparing features for {len(df)} records")
    
    df = df.copy()
    
    # Create base features
    df = create_price_features(df)
    df = create_volume_features(df)
    df = create_time_features(df)
    
    # Create lag features for close price
    df = create_lag_features(df, 'close', [1, 2, 3, 5, 7, 14])
    
    # Create lag features for daily return
    if 'daily_return' in df.columns:
        df = create_lag_features(df, 'daily_return', [1, 2, 3, 5])
    
    # Create rolling features
    df = create_rolling_features(df, 'close', [5, 10, 20])
    df = create_rolling_features(df, 'volume', [5, 10])
    
    # Fill NaN values
    df = df.fillna(method='bfill').fillna(0)
    
    logger.info(f"Created {len(df.columns)} features")
    
    return df


def get_feature_columns() -> List[str]:
    """
    Get list of feature columns for the model.
    
    Returns:
        List of column names to use as features
    """
    return [
        # Price features
        'open', 'high', 'low', 'close', 'volume',
        'daily_return', 'ma_7', 'ma_20',
        'volatility', 'momentum',
        'price_range', 'price_range_pct',
        'gap', 'gap_pct', 'close_position',
        
        # Volume features
        'volume_change', 'volume_ratio',
        
        # Time features
        'day_of_week', 'day_of_month', 'month',
        
        # Lag features
        'close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5', 'close_lag_7',
        'daily_return_lag_1', 'daily_return_lag_2', 'daily_return_lag_3',
        
        # Rolling features
        'close_roll_mean_5', 'close_roll_mean_10', 'close_roll_mean_20',
        'close_roll_std_5', 'close_roll_std_10',
    ]


def prepare_training_data(df: pd.DataFrame, target_days: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare training data for the model.
    
    Args:
        df: DataFrame with all features
        target_days: Number of days ahead to predict
    
    Returns:
        Tuple of (X, y) arrays
    """
    if df.empty:
        return np.array([]), np.array([])
    
    # Create target: future close price
    df['target'] = df['close'].shift(-target_days)
    
    # Remove rows without target
    df = df.dropna(subset=['target'])
    
    # Get feature columns that exist in DataFrame
    feature_cols = [col for col in get_feature_columns() if col in df.columns]
    
    X = df[feature_cols].values
    y = df['target'].values
    
    return X, y
