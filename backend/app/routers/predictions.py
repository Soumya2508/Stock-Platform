"""
Predictions API router.

Provides endpoints for ML-based stock price predictions.

Endpoints:
- GET /predict/{symbol}: Get price prediction for a stock
- POST /predict/train: Train models for all stocks
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import logging

from app.config import STOCK_SYMBOLS, COMPANY_NAMES, PREDICTION_DAYS
from app.schemas.prediction import PredictionResponse, ModelInfoResponse, ModelTrainingResult
from app.services.data_fetcher import fetch_stock_data
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics
from app.ml.predictor import predict_next_prices
from app.ml.model_trainer import train_model, train_all_models, load_model
from app.services.cache_service import (
    predictions_cache,
    get_cached,
    set_cached
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.get("/{symbol}", response_model=PredictionResponse)
async def get_prediction(symbol: str, days: int = PREDICTION_DAYS):
    """
    Get price prediction for a stock.
    
    Uses XGBoost model to predict future prices with confidence intervals.
    
    Args:
        symbol: Stock ticker symbol (e.g., TCS.NS)
        days: Number of days to predict (default: 7)
    
    Returns:
        Predictions with confidence bands and trend analysis
    """
    # Normalize symbol
    if not symbol.endswith('.NS'):
        symbol = f"{symbol}.NS"
    
    if symbol not in STOCK_SYMBOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found"
        )
    
    cache_key = f"prediction:{symbol}:{days}"
    
    # Check cache
    cached = get_cached(predictions_cache, cache_key)
    if cached:
        return cached
    
    # Check if model exists
    model = load_model(symbol)
    
    if model is None:
        # Train model on the fly if not available
        logger.info(f"Training model for {symbol} on demand")
        df = fetch_stock_data(symbol, period="1y")
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch data for model training"
            )
        
        df = clean_stock_data(df)
        df = calculate_all_metrics(df)
        
        training_result = train_model(df, symbol)
        
        if training_result.get('status') != 'success':
            raise HTTPException(
                status_code=500,
                detail=f"Model training failed: {training_result.get('error', 'Unknown error')}"
            )
    
    # Fetch latest data for prediction
    df = fetch_stock_data(symbol, period="1y")
    
    if df is None or df.empty:
        raise HTTPException(
            status_code=503,
            detail="Unable to fetch data for prediction"
        )
    
    df = clean_stock_data(df)
    df = calculate_all_metrics(df)
    
    # Generate prediction
    prediction = predict_next_prices(df, symbol, days)
    
    if 'error' in prediction:
        raise HTTPException(
            status_code=500,
            detail=prediction['error']
        )
    
    response = PredictionResponse(**prediction)
    
    # Cache response
    set_cached(predictions_cache, cache_key, response)
    
    return response


@router.post("/train", response_model=ModelInfoResponse)
async def train_all_stock_models(background_tasks: BackgroundTasks):
    """
    Train prediction models for all stocks.
    
    This endpoint triggers model training for all configured stocks.
    Training happens in the background and results are returned immediately.
    
    Note: Initial training may take a few minutes.
    """
    logger.info("Starting model training for all stocks")
    
    results = {}
    models_trained = []
    
    for symbol in STOCK_SYMBOLS:
        df = fetch_stock_data(symbol, period="1y")
        
        if df is None or df.empty:
            results[symbol] = ModelTrainingResult(
                symbol=symbol,
                status='failed',
                error='Unable to fetch data'
            )
            continue
        
        df = clean_stock_data(df)
        df = calculate_all_metrics(df)
        
        training_result = train_model(df, symbol)
        
        results[symbol] = ModelTrainingResult(**training_result)
        
        if training_result.get('status') == 'success':
            models_trained.append(symbol)
    
    return ModelInfoResponse(
        total_models=len(STOCK_SYMBOLS),
        models_trained=models_trained,
        training_results=results
    )


@router.get("/status/{symbol}")
async def get_model_status(symbol: str):
    """
    Check if a trained model exists for a stock.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Model status information
    """
    # Normalize symbol
    if not symbol.endswith('.NS'):
        symbol = f"{symbol}.NS"
    
    if symbol not in STOCK_SYMBOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found"
        )
    
    model = load_model(symbol)
    
    return {
        'symbol': symbol,
        'model_exists': model is not None,
        'name': COMPANY_NAMES.get(symbol, symbol)
    }
