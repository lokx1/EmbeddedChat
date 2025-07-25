# Rate limiting middleware
import asyncio
import time
from typing import Callable, Dict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = settings.RATE_LIMIT_REQUESTS, period: int = settings.RATE_LIMIT_PERIOD):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, Dict] = {}
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Initialize client data if not exists
        if client_ip not in self.clients:
            self.clients[client_ip] = {
                "requests": [],
                "blocked_until": 0
            }
        
        client_data = self.clients[client_ip]
        
        # Check if client is still blocked
        if current_time < client_data["blocked_until"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later."
            )
        
        # Clean old requests
        client_data["requests"] = [
            req_time for req_time in client_data["requests"]
            if current_time - req_time < self.period
        ]
        
        # Check rate limit
        if len(client_data["requests"]) >= self.calls:
            client_data["blocked_until"] = current_time + self.period
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds."
            )
        
        # Add current request
        client_data["requests"].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(self.calls - len(client_data["requests"]))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))
        
        return response


def add_rate_limit_middleware(app):
    """Add rate limiting middleware to FastAPI app"""
    app.add_middleware(RateLimitMiddleware)
