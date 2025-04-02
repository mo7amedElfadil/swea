"""Module to handle caching of responses dynamically."""

from functools import wraps
from typing import Callable, List

import redis
from flask import request

from app.extensions import cache
from config import Config


def generate_cache_key(func_name: str) -> str:
    """Generate a cache key using the function name and relevant request arguments."""
    key_parts = [func_name]

    for k, v in sorted(request.args.items()):  # Sorted for consistency
        key_parts.append(f"{k}-{v}")

    return "_".join(key_parts)


def cache_response(timeout: int = Config.CACHE_DEFAULT_TIMEOUT) -> Callable:
    """Decorator to cache responses dynamically with consistent key generation."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(func.__name__)
            cached_data = cache.get(cache_key)

            if cached_data:
                return cached_data

            response = func(*args, **kwargs)
            cache.set(cache_key, response, timeout=timeout)
            return response

        return wrapper

    return decorator


def invalidate_cache(func_names: List[str]) -> None:
    """
    Invalidate cache entries for a given list of function names.

    - Uses wildcard matching to find and remove cache keys.
    - Uses Redis `unlink()` instead of `delete()` for non-blocking deletion.
    - Uses `pipeline()` for batch deletion, reducing network round trips.
    """

    if Config.CACHE_TYPE != "redis":
        return

    redis_conn = redis.Redis.from_url(Config.CACHE_REDIS_URL)
    patterns = [
        f"{Config.CACHE_KEY_PREFIX}{func_name}*" for func_name in func_names
    ]

    with redis_conn.pipeline() as pipe:  # Batch operations
        for pattern in patterns:
            for key in redis_conn.scan_iter(pattern, count=1000):
                pipe.unlink(key)
        pipe.execute()
