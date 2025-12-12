"""
Pydantic schemas for Company-related API responses.

Defines data models for company information endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CompanyBase(BaseModel):
    """Base company information."""
    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company full name")


class CompanyInfo(CompanyBase):
    """Company with current market data."""
    current_price: Optional[float] = Field(None, description="Latest closing price")
    daily_change: Optional[float] = Field(None, description="Daily change percentage")
    
    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Response for company list endpoint."""
    count: int = Field(..., description="Number of companies")
    companies: List[CompanyInfo]
