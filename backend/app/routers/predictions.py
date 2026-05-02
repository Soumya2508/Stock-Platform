"""
Predictions API router.

Provides endpoints for ML-based stock price predictions.

Endpoints:
- GET /predict/{symbol}: Get price prediction for a stock
- POST /predict/train: Train models for all stocks
- All data served from SQLite
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Optional
import logging
from sqlalchemy.orm import Session

from app.config import STOCK_SYMBOLS, COMPANY_NAMES, PREDICTION_DAYS
from app.schemas.prediction import PredictionResponse, ModelInfoResponse, ModelTrainingResult
from app.database.connection import get_db
from app.services.data_fetcher import get_stock_data_df
from app.services.data_cleaner import clean_stock_data
from app.services.metrics_calculator import calculate_all_metrics
from app.ml.predictor import predict_next_prices
from app.ml.model_trainer import train_model, train_all_models, load_model

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.get("/{symbol}", response_model=PredictionResponse)
async def get_prediction(
    symbol: str,
    days: int = PREDICTION_DAYS,
    db: Session = Depends(get_db),
):
    """
    Get price prediction for a stock.

    Uses XGBoost model to predict future prices with confidence intervals.

    Args:
        symbol: Stock ticker symbol (e.g., TCS.NS)
        days: Number of days to predict (default: 7)
    """
    # Normalize symbol
    if not symbol.endswith('.NS'):
        symbol = f"{symbol}.NS"

    if symbol not in STOCK_SYMBOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found"
        )

    # Check if model exists
    model = load_model(symbol)

    if model is None:
        # Train model on the fly using SQLite data
        logger.info(f"Training model for {symbol} on demand")
        df = get_stock_data_df(db, symbol, 365)

        if df.empty:
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

    # Fetch latest data for prediction from SQLite
    df = get_stock_data_df(db, symbol, 365)

    if df.empty:
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

    return PredictionResponse(**prediction)


@router.post("/train", response_model=ModelInfoResponse)
async def train_all_stock_models(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Train prediction models for all stocks.

    Uses data from SQLite (seeded from static JSON).
    """
    logger.info("Starting model training for all stocks")

    results = {}
    models_trained = []

    for symbol in STOCK_SYMBOLS:
        df = get_stock_data_df(db, symbol, 365)

        if df.empty:
            results[symbol] = ModelTrainingResult(
                symbol=symbol,
                status='failed',
                error='No data available'
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
        training_results=results,
    )


@router.get("/status/{symbol}")
async def get_model_status(symbol: str):
    """
    Check if a trained model exists for a stock.

    Args:
        symbol: Stock ticker symbol
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
