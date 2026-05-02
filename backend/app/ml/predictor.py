"""
Prediction service for generating stock price forecasts.

This module provides:
- Price predictions for individual stocks
- Confidence intervals for predictions
- Prediction explanation

Challenges:
- Prediction uncertainty estimation
- Handling missing or incomplete feature data
- Real-time prediction latency

Future Improvements:
- Add ensemble predictions
- Implement prediction confidence calibration
- Add prediction history tracking
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import date, timedelta
import logging

from app.ml.model_trainer import load_model
from app.ml.feature_engineer import prepare_features, get_feature_columns
from app.config import PREDICTION_DAYS

logger = logging.getLogger(__name__)


def predict_next_prices(
    df: pd.DataFrame, 
    symbol: str, 
    days: int = PREDICTION_DAYS
) -> Optional[Dict]:
    """
    Predict future prices for a stock.
    
    Args:
        df: Historical data with all metrics
        symbol: Stock symbol
        days: Number of days to predict
    
    Returns:
        Dictionary with predictions or None if prediction fails
    """
    logger.info(f"Generating {days}-day prediction for {symbol}")
    
    # Load model
    model = load_model(symbol)
    if model is None:
        return {'error': f'No trained model found for {symbol}'}
    
    if df.empty:
        return {'error': 'No data available for prediction'}
    
    # Prepare features from historical data
    df_features = prepare_features(df.copy())
    
    if df_features.empty:
        return {'error': 'Feature preparation failed'}
    
    # Get feature columns
    feature_cols = [col for col in get_feature_columns() if col in df_features.columns]
    
    # Initialize predictions
    predictions = []
    confidence_lower = []
    confidence_upper = []
    
    # Get the last row for initial prediction
    current_features = df_features[feature_cols].iloc[-1:].values
    last_close = float(df_features['close'].iloc[-1])
    last_date = df_features['date'].iloc[-1]
    
    # Estimate prediction std from historical daily returns
    if 'daily_return' in df_features.columns:
        daily_std = df_features['daily_return'].std()
    else:
        daily_std = 2.0  # Default 2% daily volatility
    
    # Generate predictions day by day
    current_price = last_close
    
    for i in range(1, days + 1):
        try:
            # Predict next price
            predicted_price = float(model.predict(current_features)[0])
            
            # Calculate confidence interval (widens with prediction horizon)
            confidence_factor = np.sqrt(i) * (daily_std / 100) * current_price
            lower = predicted_price - 1.96 * confidence_factor  # 95% CI
            upper = predicted_price + 1.96 * confidence_factor
            
            predictions.append(round(predicted_price, 2))
            confidence_lower.append(round(max(0, lower), 2))
            confidence_upper.append(round(upper, 2))
            
            # Update features for next prediction (simplified)
            current_price = predicted_price
            
        except Exception as e:
            logger.error(f"Prediction error for day {i}: {str(e)}")
            break
    
    if not predictions:
        return {'error': 'Prediction failed'}
    
    # Calculate prediction dates (skip weekends)
    prediction_dates = []
    current_date = last_date if isinstance(last_date, date) else date.today()
    
    for _ in range(days):
        current_date = current_date + timedelta(days=1)
        # Skip weekends
        while current_date.weekday() >= 5:
            current_date = current_date + timedelta(days=1)
        prediction_dates.append(str(current_date))
    
    # Calculate expected return
    expected_return = ((predictions[-1] - last_close) / last_close * 100)
    
    # Determine trend
    if expected_return > 2:
        trend = 'bullish'
    elif expected_return < -2:
        trend = 'bearish'
    else:
        trend = 'neutral'
    
    return {
        'symbol': symbol,
        'current_price': round(last_close, 2),
        'prediction_days': days,
        'predictions': predictions,
        'dates': prediction_dates,
        'confidence': {
            'lower': confidence_lower,
            'upper': confidence_upper
        },
        'summary': {
            'expected_price': predictions[-1],
            'expected_return': round(expected_return, 2),
            'trend': trend,
            'min_prediction': min(predictions),
            'max_prediction': max(predictions)
        }
    }


def get_prediction_confidence_score(symbol: str) -> float:
    """
    Get confidence score for a model's predictions.
    
    Based on model's historical accuracy metrics.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Confidence score (0-100)
    """
    # This could be enhanced to use actual backtesting results
    # For now, return a reasonable default
    return 75.0


def batch_predict(
    stock_data: Dict[str, pd.DataFrame], 
    days: int = PREDICTION_DAYS
) -> Dict:
    """
    Generate predictions for all stocks.
    
    Args:
        stock_data: Dictionary mapping symbol to DataFrame
        days: Number of days to predict
    
    Returns:
        Dictionary with predictions for all stocks
    """
    results = {}
    
    for symbol, df in stock_data.items():
        prediction = predict_next_prices(df, symbol, days)
        results[symbol] = prediction
    
    successful = sum(1 for r in results.values() if 'predictions' in r)
    logger.info(f"Generated predictions for {successful}/{len(stock_data)} stocks")
    
    return results
