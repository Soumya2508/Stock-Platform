"""
XGBoost model training module.

This module handles:
- Model training
- Model persistence (save/load)
- Model evaluation

Challenges:
- Avoiding overfitting on limited data
- Handling time series cross-validation properly
- Hyperparameter tuning

Future Improvements:
- Add hyperparameter optimization
- Implement time series cross-validation
- Add model versioning
"""

import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

from app.config import MODEL_PATH
from app.ml.feature_engineer import prepare_features, prepare_training_data, get_feature_columns

logger = logging.getLogger(__name__)

# Ensure model directory exists
MODEL_PATH.mkdir(parents=True, exist_ok=True)


def get_model_path(symbol: str) -> Path:
    """
    Get the path for a model file.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Path to model file
    """
    # Clean symbol for filename
    clean_symbol = symbol.replace('.', '_').replace('/', '_')
    return MODEL_PATH / f"model_{clean_symbol}.joblib"


def train_model(
    df: pd.DataFrame, 
    symbol: str,
    test_size: float = 0.2
) -> Dict:
    """
    Train XGBoost model for a stock.
    
    Args:
        df: DataFrame with stock data and calculated metrics
        symbol: Stock symbol
        test_size: Fraction of data to use for testing
    
    Returns:
        Dictionary with training results
    """
    logger.info(f"Training model for {symbol}")
    
    if df.empty or len(df) < 50:
        return {'error': 'Insufficient data for training', 'symbol': symbol}
    
    # Prepare features
    df_features = prepare_features(df)
    
    # Prepare training data
    X, y = prepare_training_data(df_features)
    
    if len(X) < 30:
        return {'error': 'Insufficient samples after feature preparation', 'symbol': symbol}
    
    # Split data (time series aware - last portion for testing)
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Initialize and train model
    model = XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective='reg:squarederror'
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # Evaluate model
    y_pred = model.predict(X_test)
    
    metrics = {
        'mae': float(mean_absolute_error(y_test, y_pred)),
        'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
        'r2': float(r2_score(y_test, y_pred)),
        'mape': float(np.mean(np.abs((y_test - y_pred) / y_test)) * 100)
    }
    
    # Save model
    model_path = get_model_path(symbol)
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")
    
    return {
        'symbol': symbol,
        'status': 'success',
        'samples': len(X),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'metrics': metrics
    }


def load_model(symbol: str) -> Optional[XGBRegressor]:
    """
    Load a trained model for a symbol.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Loaded model or None if not found
    """
    model_path = get_model_path(symbol)
    
    if not model_path.exists():
        logger.warning(f"No model found for {symbol}")
        return None
    
    try:
        model = joblib.load(model_path)
        logger.info(f"Model loaded for {symbol}")
        return model
    except Exception as e:
        logger.error(f"Error loading model for {symbol}: {str(e)}")
        return None


def train_all_models(stock_data: Dict[str, pd.DataFrame]) -> Dict:
    """
    Train models for all stocks.
    
    Args:
        stock_data: Dictionary mapping symbol to DataFrame
    
    Returns:
        Dictionary with training results for all stocks
    """
    results = {}
    
    for symbol, df in stock_data.items():
        result = train_model(df, symbol)
        results[symbol] = result
    
    successful = sum(1 for r in results.values() if r.get('status') == 'success')
    logger.info(f"Trained {successful}/{len(stock_data)} models successfully")
    
    return results


def get_feature_importance(symbol: str) -> Optional[Dict]:
    """
    Get feature importance from a trained model.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Dictionary mapping feature names to importance scores
    """
    model = load_model(symbol)
    
    if model is None:
        return None
    
    feature_names = get_feature_columns()
    importances = model.feature_importances_
    
    # Handle case where feature counts don't match
    min_len = min(len(feature_names), len(importances))
    
    importance_dict = dict(zip(feature_names[:min_len], importances[:min_len].tolist()))
    
    # Sort by importance
    sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    return sorted_importance
