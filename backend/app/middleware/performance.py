from fastapi import Request
import time
from ..core.monitoring import metrics

async def performance_middleware(request: Request, call_next):
    # Get country from request
    country = request.path_params.get("country", "nigeria")
    
    # Start timing
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Track metrics
    metrics.track_request(country, request.url.path)
    metrics.track_request_duration(country, request.url.path, duration)
    
    # Add performance headers
    response.headers["X-Response-Time"] = str(duration)
    
    return response 