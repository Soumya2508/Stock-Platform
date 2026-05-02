"""
Utility helper functions.

This module contains general-purpose helper functions
used across the application.

Challenges:
- Handling timezone conversions
- Date format standardization

Future Improvements:
- Add more date/time utilities
- Add logging utilities
"""

from datetime import datetime, date, timedelta
from typing import Union, Optional
import logging


def format_date(d: Union[datetime, date, str]) -> str:
    """
    Format date to ISO string format (YYYY-MM-DD).
    
    Args:
        d: Date in various formats
    
    Returns:
        Formatted date string
    """
    if isinstance(d, datetime):
        return d.strftime('%Y-%m-%d')
    elif isinstance(d, date):
        return d.strftime('%Y-%m-%d')
    elif isinstance(d, str):
        return d[:10]  # Assume ISO format
    return str(d)


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string to date object.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
    
    Returns:
        Date object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def get_date_range(days: int) -> tuple:
    """
    Get date range from today going back N days.
    
    Args:
        days: Number of days to go back
    
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number with thousand separators.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format number as percentage.
    
    Args:
        value: Number to format (already in percentage)
        decimals: Number of decimal places
    
    Returns:
        Formatted string with % sign
    """
    sign = '+' if value > 0 else ''
    return f"{sign}{value:.{decimals}f}%"


def format_volume(volume: int) -> str:
    """
    Format volume with K/M/B suffixes.
    
    Args:
        volume: Volume number
    
    Returns:
        Formatted string (e.g., "1.5M")
    """
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.1f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.1f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.1f}K"
    return str(volume)


def setup_logging(level: int = logging.INFO):
    """
    Set up application logging.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
