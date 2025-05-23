"""Rate limiting module"""

from functools import wraps
from typing import Any, Callable, List, Optional, Union

from flask import request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config

# Initialize limiter
limiter = Limiter(
    get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri=Config.LIMITER_REDIS_URL,
)


def init_limiter(app):
    """Initialize the limiter with the Flask app"""
    limiter.init_app(app)


def rate_limit(
    limits: Optional[Union[List[str], str]] = None,
    key_func: Optional[Callable[[], str]] = None,
    exempt_when: Optional[Callable[[], bool]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for rate limiting specific routes

    Args:
        limits (list or str): List of rate limit strings or a single string
        key_func (callable): Function to extract the key for rate limiting
        exempt_when (callable): Function that returns True when rate limiting should be exempt

    Returns:
        decorator: A decorator to apply rate limiting to a route

    Examples:
        Basic usage with direct limit specification:
        ```python
        @app.route('/api/comments')
        @rate_limit("5 per minute")
        def post_comment():
            # This endpoint is limited to 5 requests per minute per IP
            return create_comment()
        ```

        Using predefined limit configurations:
        ```python
        @app.route('/api/user-profile')
        @rate_limit(RateLimits.NORMAL)
        def get_user_profile():
            # This endpoint uses the NORMAL rate limit configuration
            return fetch_profile()
        ```

        Exempting certain users:
        ```python
        @app.route('/api/data-export')
        @rate_limit("2 per day", exempt_when=RateLimits.exempt_for_admins)
        def export_data():
            # Regular users limited to 2 exports per day
            # Admin users are exempt from this limit
            return generate_export()
        ```

        Combined approach for sensitive endpoints:
        ```python
        @app.route('/api/password-reset')
        @rate_limit(
            RateLimits.STRICT,
            key_func=RateLimits.get_key_by_ip_and_path,
            exempt_when=RateLimits.exempt_for_admins
        )
        def reset_password():
            # Uses strict limits, identified by IP+path, exempts admins
            return process_password_reset()
        ```
    """
    # Convert list of limits to comma-separated string if it's a list
    if isinstance(limits, list):
        limits_str = ", ".join(limits)
    else:
        limits_str = limits

    def decorator(f):
        @wraps(f)
        @limiter.limit(limits_str, key_func=key_func, exempt_when=exempt_when)  # type: ignore
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    return decorator


class RateLimits:
    """Common rate limit configurations"""

    DEFAULT = Config.RATE_LIMITS["DEFAULT"]
    STRICT = Config.RATE_LIMITS["STRICT"]
    NORMAL = Config.RATE_LIMITS["NORMAL"]
    LENIENT = Config.RATE_LIMITS["LENIENT"]
    API = Config.RATE_LIMITS["API"]

    # Custom key functions
    @staticmethod
    def get_key_by_ip_and_endpoint() -> str:
        """Rate limit based on both IP and endpoint"""
        return f"{get_remote_address()}:{request.endpoint}"

    @staticmethod
    def get_key_by_ip_and_path() -> str:
        """Rate limit based on both IP and path"""
        return f"{get_remote_address()}:{request.path}"

    @staticmethod
    def exempt_for_admins() -> bool:
        """Exempt admins from rate limiting"""

        return session.get("is_admin", False)
