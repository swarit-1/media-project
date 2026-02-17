"""
Simple in-memory rate limiter using a sliding window counter.
For production, replace with Redis-backed implementation.
"""

import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class _SlidingWindow:
    """Sliding window counter for rate limiting."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds

        # Prune old entries
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

        if len(self._requests[key]) >= self.max_requests:
            return False

        self._requests[key].append(now)
        return True

    def remaining(self, key: str) -> int:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        return max(0, self.max_requests - len(self._requests[key]))


# Global rate limiters keyed by name
_limiters: dict[str, _SlidingWindow] = {}


def _get_limiter(name: str, max_requests: int, window_seconds: int) -> _SlidingWindow:
    if name not in _limiters:
        _limiters[name] = _SlidingWindow(max_requests, window_seconds)
    return _limiters[name]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Path-prefix based rate limiting middleware.

    Usage:
        app.add_middleware(
            RateLimitMiddleware,
            rules={
                "/api/v1/auth/": (20, 60),      # 20 req/min
                "/api/v1/discovery/": (60, 60),  # 60 req/min
            }
        )
    """

    def __init__(self, app, rules: dict[str, tuple[int, int]] | None = None):
        super().__init__(app)
        self.rules = rules or {}
        self._limiters = {
            prefix: _SlidingWindow(max_req, window)
            for prefix, (max_req, window) in self.rules.items()
        }

    def _get_client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        for prefix, limiter in self._limiters.items():
            if request.url.path.startswith(prefix):
                key = self._get_client_key(request)
                if not limiter.is_allowed(key):
                    return Response(
                        content='{"detail":"Rate limit exceeded"}',
                        status_code=429,
                        media_type="application/json",
                        headers={"Retry-After": str(limiter.window_seconds)},
                    )
                break

        return await call_next(request)


def rate_limit(name: str, max_requests: int = 30, window_seconds: int = 60):
    """
    Decorator-based rate limiter for individual endpoints.

    Usage:
        @router.post("/login")
        @rate_limit("login", max_requests=10, window_seconds=60)
        async def login(request: Request, ...):
            ...
    """

    def decorator(func: Callable):
        limiter = _get_limiter(name, max_requests, window_seconds)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find Request in args/kwargs
            request: Optional[Request] = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                forwarded = request.headers.get("x-forwarded-for")
                if forwarded:
                    client_ip = forwarded.split(",")[0].strip()
                else:
                    client_ip = request.client.host if request.client else "unknown"

                if not limiter.is_allowed(client_ip):
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later.",
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
