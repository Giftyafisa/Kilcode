import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.admin_config import admin_settings
from app.api.v1.endpoints import admin_auth, admin_dashboard, admin_users, admin_payments, admin_betting, admin_statistics
from app.db.base import Base  # Import Base
from app.core.database import engine  # Import engine
import logging
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Admin API")

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:8001",
    "http://127.0.0.1:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Main backend URL
MAIN_BACKEND_URL = "http://localhost:8000"

# HTTP client for forwarding requests
async def get_http_client():
    async with httpx.AsyncClient() as client:
        return client

# Add this middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

# Include admin routes
app.include_router(admin_auth.router, prefix="/api/v1/admin")
app.include_router(admin_dashboard.router, prefix="/api/v1/admin")
app.include_router(admin_users.router, prefix="/api/v1/admin")
app.include_router(admin_payments.router, prefix="/api/v1/admin")
app.include_router(admin_betting.router, prefix="/api/v1/admin")
app.include_router(admin_statistics.router, prefix="/api/v1/admin")

# Proxy middleware for forwarding requests to main backend
@app.middleware("http")
async def proxy_middleware(request: Request, call_next):
    path = request.url.path
    
    # Handle admin-specific routes directly
    if path.startswith("/api/v1/admin"):
        return await call_next(request)
    
    # Forward other requests to main backend
    if path.startswith("/api"):
        try:
            client = httpx.AsyncClient()
            url = f"{MAIN_BACKEND_URL}{path}"
            
            # Get request body if present
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]},
                content=body,
                params=request.query_params,
            )
            
            # Create FastAPI Response from httpx response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except Exception as e:
            logger.error(f"Error forwarding request: {str(e)}")
            raise HTTPException(status_code=500, detail="Error forwarding request")
        finally:
            await client.aclose()
    
    return await call_next(request)

# Debug endpoint to list all routes
@app.get("/routes")
async def list_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "methods": route.methods,
            "name": route.name
        })
    return {"routes": routes}

@app.get("/test")
async def test_endpoint():
    return {"message": "Admin server is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check main backend connection
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_BACKEND_URL}/health")
            main_backend_status = response.status_code == 200
    except:
        main_backend_status = False

    return {
        "status": "healthy",
        "main_backend_connected": main_backend_status,
        "admin_server": "running"
    }

if __name__ == "__main__":
    port = admin_settings.ADMIN_API_PORT
    logger.info(f"Starting admin server on port {port}...")
    uvicorn.run(
        "admin_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="debug"
    ) 