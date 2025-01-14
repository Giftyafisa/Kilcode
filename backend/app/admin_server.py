from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from sqlalchemy import create_engine, text
from app.db.base import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create admin engine
admin_engine = create_engine(settings.ADMIN_DATABASE_URL)

app = FastAPI(
    title="Kilcode Admin API",
    description="Admin API for Kilcode betting code verification platform",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:5174",  # Admin frontend
    "http://127.0.0.1:5174",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up admin server...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize database
    logger.info("Initializing admin database...")
    try:
        # Create database tables
        Base.metadata.create_all(bind=admin_engine)
        logger.info("Database tables created successfully")
        
        # Verify database connection
        with admin_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection verified")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

    logger.info("Admin server startup complete")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.ADMIN_API_PORT) 