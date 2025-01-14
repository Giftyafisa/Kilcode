import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.admin_config import admin_settings
from app.api.v1.endpoints import payment_admin_auth, admin_payments
from app.db.base import Base
from app.core.database import admin_engine
from app.core.auth import get_current_admin
from app.models.admin import Admin, CountryEnum
import logging
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=admin_engine)

app = FastAPI(title="Payment Admin API")

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:8002",
    "http://127.0.0.1:8002"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Country-specific middleware
@app.middleware("http")
async def country_specific_middleware(request: Request, call_next):
    try:
        # Skip middleware for auth routes and health checks
        if any(path in str(request.url.path) for path in ["/auth/", "/health", "/test", "/routes"]):
            return await call_next(request)

        # Get current admin from request state (set by auth dependency)
        admin: Admin = getattr(request.state, "current_admin", None)
        if not admin:
            return await call_next(request)

        # Super admins can access all countries
        if admin.role == "super_admin":
            return await call_next(request)

        # Add country to request state for use in endpoints
        request.state.admin_country = admin.country
        
        # Country admins can only access their country's data
        if "country" in request.query_params:
            if request.query_params["country"].lower() != admin.country.lower():
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. You can only access {admin.country} data."
                )

        return await call_next(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in country middleware: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include payment admin auth routes
app.include_router(
    payment_admin_auth.router,
    prefix="/api/v1/payment-admin/auth",
    tags=["payment-admin-auth"]
)

# Include payment admin routes with admin dependency
app.include_router(
    admin_payments.router,
    prefix="/api/v1/payment-admin",
    tags=["payment-admin"],
    dependencies=[Depends(get_current_admin)]
)

# Debug endpoint
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
    return {"message": "Payment Admin server is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "payment_admin_server": "running",
        "supported_countries": [country.value for country in CountryEnum]
    }

if __name__ == "__main__":
    port = 8002  # Different port for payment admin
    logger.info(f"Starting payment admin server on port {port}...")
    uvicorn.run(
        "payment_admin_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="debug"
    ) 