"""
Configuration settings for the Stock Intelligence Dashboard backend.

This module centralizes all configuration parameters including:
- Database settings
- API configuration
- Stock symbols list
- Cache settings
"""

from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/stocks.db"
DATABASE_PATH = BASE_DIR / "data" / "stocks.db"

# Stock symbols (NSE)
STOCK_SYMBOLS = [
    "TCS.NS",
    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "WIPRO.NS",
    "ITC.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "HINDUNILVR.NS",
    "BAJFINANCE.NS",
    "MARUTI.NS",
    "LT.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
]

# Company display names
COMPANY_NAMES = {
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "RELIANCE.NS": "Reliance Industries",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "WIPRO.NS": "Wipro",
    "ITC.NS": "ITC Limited",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "BAJFINANCE.NS": "Bajaj Finance",
    "MARUTI.NS": "Maruti Suzuki",
    "LT.NS": "Larsen & Toubro",
    "AXISBANK.NS": "Axis Bank",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
}

# API Configuration
API_TITLE = "Stock Intelligence Dashboard API"
API_DESCRIPTION = "REST API for stock market data, analytics, and ML predictions"
API_VERSION = "1.0.0"

# Data settings
DATA_PERIOD = "1y"  # 1 year of historical data
DEFAULT_DAYS = 30   # Default days for data endpoint

# Cache settings (TTL in seconds)
CACHE_TTL_COMPANIES = 300      # 5 minutes
CACHE_TTL_STOCK_DATA = 300     # 5 minutes
CACHE_TTL_PREDICTIONS = 3600   # 1 hour

# ML settings
PREDICTION_DAYS = 7  # Predict next 7 days
MODEL_PATH = BASE_DIR / "ml_models"
