from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable
from .config import settings

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "message": str(e) if settings.ENV == "development" else "An error occurred"
                }
            )

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = {}

    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old requests
        self.requests = {ip: reqs for ip, reqs in self.requests.items() 
                        if current_time - reqs[-1] < 60}
        
        if client_ip in self.requests:
            if len(self.requests[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            self.requests[client_ip].append(current_time)
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)
