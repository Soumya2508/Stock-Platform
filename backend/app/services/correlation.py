"""
Correlation analysis service for comparing stocks.

This module provides:
- Pairwise correlation calculation
- Correlation matrix generation
- Performance comparison between stocks

Challenges:
- Aligning dates across different stocks
- Handling stocks with different trading histories
- Correlation doesn't imply causation

Future Improvements:
- Add rolling correlation analysis
- Implement lead-lag correlation
- Add sector-based correlation grouping
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_pairwise_correlation(
    df1: pd.DataFrame, 
    df2: pd.DataFrame,
    column: str = 'close'
) -> float:
    """
    Calculate correlation between two stocks.
    
    Args:
        df1: First stock DataFrame
        df2: Second stock DataFrame
        column: Column to use for correlation (default: 'close')
    
    Returns:
        Pearson correlation coefficient (-1 to 1)
    """
    if df1.empty or df2.empty:
        return 0.0
    
    # Merge on date to align the data
    merged = pd.merge(
        df1[['date', column]].rename(columns={column: 'stock1'}),
        df2[['date', column]].rename(columns={column: 'stock2'}),
        on='date',
        how='inner'
    )
    
    if len(merged) < 10:  # Need minimum data points
        logger.warning("Insufficient overlapping data for correlation")
        return 0.0
    
    correlation = merged['stock1'].corr(merged['stock2'])
    
    return round(correlation, 4) if not np.isnan(correlation) else 0.0


def calculate_returns_correlation(
    df1: pd.DataFrame, 
    df2: pd.DataFrame
) -> float:
    """
    Calculate correlation based on daily returns.
    
    Returns correlation is often more meaningful than price correlation
    as it removes the trend component.
    
    Args:
        df1: First stock DataFrame with 'daily_return' column
        df2: Second stock DataFrame with 'daily_return' column
    
    Returns:
        Correlation coefficient of daily returns
    """
    return calculate_pairwise_correlation(df1, df2, 'daily_return')


def compare_stocks(
    df1: pd.DataFrame, 
    df2: pd.DataFrame,
    symbol1: str,
    symbol2: str
) -> Dict:
    """
    Generate comparison metrics between two stocks.
    
    Args:
        df1: First stock DataFrame
        df2: Second stock DataFrame
        symbol1: First stock symbol
        symbol2: Second stock symbol
    
    Returns:
        Dictionary with comparison metrics
    """
    if df1.empty or df2.empty:
        return {'error': 'Insufficient data for comparison'}
    
    # Merge data on date
    merged = pd.merge(
        df1[['date', 'close', 'daily_return', 'volume']].rename(
            columns={'close': 'close1', 'daily_return': 'return1', 'volume': 'volume1'}
        ),
        df2[['date', 'close', 'daily_return', 'volume']].rename(
            columns={'close': 'close2', 'daily_return': 'return2', 'volume': 'volume2'}
        ),
        on='date',
        how='inner'
    )
    
    if len(merged) < 10:
        return {'error': 'Insufficient overlapping data'}
    
    # Calculate normalized prices (percentage change from start)
    start_price1 = merged['close1'].iloc[0]
    start_price2 = merged['close2'].iloc[0]
    
    merged['normalized1'] = ((merged['close1'] / start_price1) - 1) * 100
    merged['normalized2'] = ((merged['close2'] / start_price2) - 1) * 100
    
    # Calculate metrics
    price_correlation = merged['close1'].corr(merged['close2'])
    returns_correlation = merged['return1'].corr(merged['return2'])
    
    # Performance comparison
    total_return1 = ((merged['close1'].iloc[-1] / start_price1) - 1) * 100
    total_return2 = ((merged['close2'].iloc[-1] / start_price2) - 1) * 100
    
    avg_return1 = merged['return1'].mean()
    avg_return2 = merged['return2'].mean()
    
    volatility1 = merged['return1'].std()
    volatility2 = merged['return2'].std()
    
    # Handle NaN values
    price_correlation = 0.0 if np.isnan(price_correlation) else price_correlation
    returns_correlation = 0.0 if np.isnan(returns_correlation) else returns_correlation
    avg_return1 = 0.0 if np.isnan(avg_return1) else avg_return1
    avg_return2 = 0.0 if np.isnan(avg_return2) else avg_return2
    volatility1 = 0.0 if np.isnan(volatility1) else volatility1
    volatility2 = 0.0 if np.isnan(volatility2) else volatility2
    
    return {
        'symbols': [symbol1, symbol2],
        'period': {
            'start': str(merged['date'].iloc[0]),
            'end': str(merged['date'].iloc[-1]),
            'days': str(len(merged))
        },
        'correlation': {
            'price': round(price_correlation, 4),
            'returns': round(returns_correlation, 4)
        },
        'performance': {
            symbol1: {
                'total_return': round(total_return1, 2),
                'avg_daily_return': round(avg_return1, 4),
                'volatility': round(volatility1, 4)
            },
            symbol2: {
                'total_return': round(total_return2, 2),
                'avg_daily_return': round(avg_return2, 4),
                'volatility': round(volatility2, 4)
            }
        },
        'chart_data': {
            'dates': merged['date'].astype(str).tolist(),
            symbol1: merged['normalized1'].round(2).tolist(),
            symbol2: merged['normalized2'].round(2).tolist()
        }
    }


def generate_correlation_matrix(
    stock_data: Dict[str, pd.DataFrame],
    column: str = 'daily_return'
) -> Dict:
    """
    Generate correlation matrix for all stocks.
    
    Args:
        stock_data: Dictionary mapping symbol to DataFrame
        column: Column to use for correlation
    
    Returns:
        Dictionary with correlation matrix data for heatmap
    """
    symbols = list(stock_data.keys())
    n = len(symbols)
    
    if n < 2:
        return {'error': 'Need at least 2 stocks for correlation matrix'}
    
    # Initialize matrix
    matrix = np.zeros((n, n))
    
    for i, sym1 in enumerate(symbols):
        for j, sym2 in enumerate(symbols):
            if i == j:
                matrix[i][j] = 1.0
            elif i < j:
                corr = calculate_pairwise_correlation(
                    stock_data[sym1], 
                    stock_data[sym2],
                    column
                )
                matrix[i][j] = corr
                matrix[j][i] = corr  # Symmetric matrix
    
    return {
        'symbols': symbols,
        'matrix': matrix.round(4).tolist()
    }
