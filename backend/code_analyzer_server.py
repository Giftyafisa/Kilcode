import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.admin_config import admin_settings
from app.api.v1.endpoints import admin_auth, admin_betting, code_analyzer
from app.db.base import Base
from app.core.database import admin_engine
from app.core.auth import get_current_admin
from app.models.admin import Admin, AdminRole
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=admin_engine)

app = FastAPI(title="Code Analyzer API")

# Configure CORS for code analyzer portal
origins = [
    "http://localhost:5176",  # Code analyzer portal
    "http://127.0.0.1:5176",
    "http://localhost:8003",  # Code analyzer backend
    "http://127.0.0.1:8003"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Code analyzer role middleware
@app.middleware("http")
async def code_analyzer_middleware(request: Request, call_next):
    try:
        # Skip middleware for auth routes and health checks
        if any(path in str(request.url.path) for path in ["/auth/", "/health"]):
            return await call_next(request)

        # Get current admin from request state
        admin: Admin = getattr(request.state, "current_admin", None)
        if not admin:
            return await call_next(request)

        # Only allow code analyzers and super admins
        if admin.role not in [AdminRole.CODE_ANALYST.value, AdminRole.SUPER_ADMIN.value]:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Only code analyzers can access this service."
            )

        # Add country to request state
        request.state.admin_country = admin.country
        
        return await call_next(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in code analyzer middleware: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include auth routes
app.include_router(
    admin_auth.router,
    prefix="/api/v1/code-analyzer/auth",
    tags=["code-analyzer-auth"]
)

# Include code analysis routes with admin dependency
app.include_router(
    code_analyzer.router,
    prefix="/api/v1/code-analyzer",
    tags=["code-analyzer"],
    dependencies=[Depends(get_current_admin)]
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "code_analyzer_server": "running",
        "database": "connected"
    }

if __name__ == "__main__":
    port = 8003  # Dedicated port for code analyzer service
    logger.info(f"Starting code analyzer server on port {port}...")
    uvicorn.run(
        "code_analyzer_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="debug"
    ) 