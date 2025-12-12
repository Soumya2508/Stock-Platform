"""
FastAPI main application entry point.

This module initializes the FastAPI application and includes:
- API router registration
- CORS middleware configuration
- Application lifespan events
- Health check endpoint

Challenges:
- CORS configuration for frontend integration
- Database initialization timing
- Graceful shutdown handling

Future Improvements:
- Add rate limiting middleware
- Implement request logging
- Add authentication middleware
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
from app.database.connection import init_db
from app.routers import companies, stock_data, summary, compare, top_movers, predictions
from app.utils.helpers import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Stock Intelligence Dashboard API")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API")


# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies.router)
app.include_router(stock_data.router)
app.include_router(summary.router)
app.include_router(compare.router)
app.include_router(top_movers.router)
app.include_router(predictions.router)


@app.get("/", tags=["Health"])
async def root():
    """
    API root endpoint / health check.
    
    Returns API status and basic information.
    """
    return {
        "status": "healthy",
        "message": "Stock Intelligence Dashboard API",
        "version": API_VERSION,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}
