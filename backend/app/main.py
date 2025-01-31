from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.websocket import router as websocket_router
from app.core.database import init_db, engine, Base
from app.db.base import Base
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    debug=True
)

# Update CORS middleware configuration
origins = [
    "https://kilcode-app.vercel.app",  # New frontend domain
    "https://kilcode-frontend-ng1ah21t9-giftyafisas-projects.vercel.app",  # Latest deployment
    "https://kilcode-frontend-55rtit4d8-giftyafisas-projects.vercel.app",
    "https://kilcode-frontend.vercel.app",
    "https://kilcode.vercel.app",
    "http://localhost:5173",
    "https://kilcode.duckdns.org",
    "https://ng-kilcode.duckdns.org",
    "https://gh-kilcode.duckdns.org",
    "http://kilcode.duckdns.org",
    "http://ng-kilcode.duckdns.org",
    "http://gh-kilcode.duckdns.org",
    "http://localhost",
    "http://localhost:8000",
    "https://localhost:8000"
] + settings.CORS_ORIGINS

logger.info(f"Configuring CORS with origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    if request.method == "OPTIONS":
        response = JSONResponse(content={})
        origin = request.headers.get("Origin")
        if origin in origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
        return response
    response = await call_next(request)
    origin = request.headers.get("Origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    logger.info(f"Response status: {response.status_code}")
    return response

# Include WebSocket router first (without prefix)
logger.info("Registering WebSocket routes")
app.include_router(websocket_router)

# Then include API router
logger.info("Registering API routes")
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API prefix: {settings.API_V1_STR}")
    
    # Initialize database on startup
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "user_id": None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True) 