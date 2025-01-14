from fastapi import Request
from fastapi.responses import JSONResponse
from ..core.security import security_manager
from ..core.config import settings
import time
import logging
from jose import jwt

logger = logging.getLogger(__name__)

async def security_middleware(request: Request, call_next):
    # Skip security checks in development
    if settings.ENVIRONMENT == "development":
        return await call_next(request)
        
    try:
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Decode token
            try:
                payload = jwt.decode(
                    token, 
                    settings.ADMIN_SECRET_KEY, 
                    algorithms=[settings.ALGORITHM]
                )
                # Allow both "admin" and "access" token types
                if payload.get("type") in ["admin", "access"]:
                    return await call_next(request)
            except Exception as e:
                logger.error(f"Token validation error: {str(e)}")
                
        country = request.path_params.get("country", "nigeria")
        await security_manager.verify_request(request, country)
        
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Security middleware error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Security check failed",
                "country": country
            }
        ) 