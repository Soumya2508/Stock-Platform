"""
Pydantic schemas for ML Prediction API responses.

Defines data models for prediction endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ConfidenceInterval(BaseModel):
    """Confidence bounds for predictions."""
    lower: List[float]
    upper: List[float]


class PredictionSummary(BaseModel):
    """Summary of prediction results."""
    expected_price: float
    expected_return: float
    trend: str  # bullish, bearish, neutral
    min_prediction: float
    max_prediction: float


class PredictionResponse(BaseModel):
    """Response for prediction endpoint."""
    symbol: str
    current_price: float
    prediction_days: int
    predictions: List[float]
    dates: List[str]
    confidence: ConfidenceInterval
    summary: PredictionSummary


class ModelTrainingResult(BaseModel):
    """Result of model training."""
    symbol: str
    status: str
    samples: Optional[int] = None
    train_samples: Optional[int] = None
    test_samples: Optional[int] = None
    metrics: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class ModelInfoResponse(BaseModel):
    """Information about trained models."""
    total_models: int
    models_trained: List[str]
    training_results: Dict[str, ModelTrainingResult]
