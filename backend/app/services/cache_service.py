"""
Caching service for API responses.

This module provides:
- In-memory caching with TTL
- Thread-safe cache operations
- Cache invalidation utilities

Challenges:
- Memory management with large datasets
- Cache consistency during data updates
- TTL tuning for optimal freshness vs performance

Future Improvements:
- Add Redis for distributed caching
- Implement cache warming on startup
- Add cache statistics and monitoring
"""

from cachetools import TTLCache
from functools import wraps
from typing import Any, Callable, Optional
import threading
import logging

from app.config import CACHE_TTL_COMPANIES, CACHE_TTL_STOCK_DATA, CACHE_TTL_PREDICTIONS

logger = logging.getLogger(__name__)

# Thread-safe caches with different TTLs
_cache_lock = threading.Lock()

# Cache instances
companies_cache = TTLCache(maxsize=100, ttl=CACHE_TTL_COMPANIES)
stock_data_cache = TTLCache(maxsize=500, ttl=CACHE_TTL_STOCK_DATA)
predictions_cache = TTLCache(maxsize=100, ttl=CACHE_TTL_PREDICTIONS)


def get_cached(cache: TTLCache, key: str) -> Optional[Any]:
    """
    Safely get value from cache.
    
    Args:
        cache: Cache instance
        key: Cache key
    
    Returns:
        Cached value or None if not found
    """
    with _cache_lock:
        return cache.get(key)


def set_cached(cache: TTLCache, key: str, value: Any) -> None:
    """
    Safely set value in cache.
    
    Args:
        cache: Cache instance
        key: Cache key
        value: Value to cache
    """
    with _cache_lock:
        cache[key] = value
        logger.debug(f"Cached key: {key}")


def delete_cached(cache: TTLCache, key: str) -> None:
    """
    Safely delete value from cache.
    
    Args:
        cache: Cache instance
        key: Cache key
    """
    with _cache_lock:
        cache.pop(key, None)


def clear_cache(cache: TTLCache) -> None:
    """
    Clear all entries from cache.
    
    Args:
        cache: Cache instance to clear
    """
    with _cache_lock:
        cache.clear()
        logger.info("Cache cleared")


def cached_response(cache: TTLCache):
    """
    Decorator for caching function responses.
    
    Usage:
        @cached_response(stock_data_cache)
        def get_stock_data(symbol: str):
            ...
    
    Args:
        cache: Cache instance to use
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = get_cached(cache, key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            set_cached(cache, key, result)
            
            return result
        
        return wrapper
    return decorator


def get_cache_stats() -> dict:
    """
    Get statistics for all caches.
    
    Returns:
        Dictionary with cache statistics
    """
    return {
        'companies': {
            'size': len(companies_cache),
            'maxsize': companies_cache.maxsize,
            'ttl': CACHE_TTL_COMPANIES
        },
        'stock_data': {
            'size': len(stock_data_cache),
            'maxsize': stock_data_cache.maxsize,
            'ttl': CACHE_TTL_STOCK_DATA
        },
        'predictions': {
            'size': len(predictions_cache),
            'maxsize': predictions_cache.maxsize,
            'ttl': CACHE_TTL_PREDICTIONS
        }
    }
