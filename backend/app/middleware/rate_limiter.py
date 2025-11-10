"""
Rate Limiting Middleware
Prevents abuse by limiting request rates per IP
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio


class RateLimiter:
    """
    Simple in-memory rate limiter

    For production, use Redis-based rate limiting (slowapi or fastapi-limiter)
    """

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Store request timestamps per IP
        # Format: {ip: [timestamp1, timestamp2, ...]}
        self.minute_requests = defaultdict(list)
        self.hour_requests = defaultdict(list)

        # Cleanup task
        self.cleanup_task = None

    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory bloat"""
        now = datetime.now()
        minute_cutoff = now - timedelta(minutes=1)
        hour_cutoff = now - timedelta(hours=1)

        # Cleanup minute tracking
        for ip in list(self.minute_requests.keys()):
            self.minute_requests[ip] = [
                ts for ts in self.minute_requests[ip] if ts > minute_cutoff
            ]
            if not self.minute_requests[ip]:
                del self.minute_requests[ip]

        # Cleanup hour tracking
        for ip in list(self.hour_requests.keys()):
            self.hour_requests[ip] = [
                ts for ts in self.hour_requests[ip] if ts > hour_cutoff
            ]
            if not self.hour_requests[ip]:
                del self.hour_requests[ip]

    def is_allowed(self, client_ip: str) -> tuple[bool, str]:
        """
        Check if request is allowed for this IP

        Returns:
            (allowed, error_message)
        """
        now = datetime.now()

        # Check minute limit
        minute_cutoff = now - timedelta(minutes=1)
        recent_minute = [ts for ts in self.minute_requests[client_ip] if ts > minute_cutoff]

        if len(recent_minute) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

        # Check hour limit
        hour_cutoff = now - timedelta(hours=1)
        recent_hour = [ts for ts in self.hour_requests[client_ip] if ts > hour_cutoff]

        if len(recent_hour) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

        # Record this request
        self.minute_requests[client_ip].append(now)
        self.hour_requests[client_ip].append(now)

        return True, ""

    async def start_cleanup_task(self):
        """Start background cleanup task"""
        while True:
            await asyncio.sleep(300)  # Cleanup every 5 minutes
            self._cleanup_old_entries()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits

    Configuration:
    - Upload endpoints: 10 requests/minute, 100 requests/hour
    - Transform endpoints: 30 requests/minute, 500 requests/hour
    - Other endpoints: 60 requests/minute, 1000 requests/hour
    """

    def __init__(self, app):
        super().__init__(app)

        # Different rate limiters for different endpoints
        self.upload_limiter = RateLimiter(requests_per_minute=10, requests_per_hour=100)
        self.transform_limiter = RateLimiter(requests_per_minute=30, requests_per_hour=500)
        self.general_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request
        Handles proxy headers (X-Forwarded-For, X-Real-IP)
        """
        # Check proxy headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"

    def _get_limiter(self, path: str) -> RateLimiter:
        """Select appropriate rate limiter based on endpoint"""
        if "/upload" in path or "/detect-file-format" in path:
            return self.upload_limiter
        elif "/transform" in path or "/export" in path:
            return self.transform_limiter
        else:
            return self.general_limiter

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Select limiter based on endpoint
        limiter = self._get_limiter(request.url.path)

        # Check rate limit
        allowed, error_message = limiter.is_allowed(client_ip)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": error_message,
                        "retry_after": 60  # seconds
                    },
                    "status": 429
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            limiter.requests_per_minute - len(limiter.minute_requests[client_ip])
        )

        return response


# Singleton instance
_rate_limiter_middleware = None


def get_rate_limiter_middleware(app):
    """Get or create rate limiter middleware"""
    global _rate_limiter_middleware
    if _rate_limiter_middleware is None:
        _rate_limiter_middleware = RateLimitMiddleware(app)
    return _rate_limiter_middleware
