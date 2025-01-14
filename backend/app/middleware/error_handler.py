from fastapi import Request
from fastapi.responses import JSONResponse
from ..core.errors import CountryError, ErrorCode, ErrorMessages

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except CountryError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=e.detail
        )
    except Exception as e:
        # Get country from request if available
        country = request.path_params.get("country", "nigeria")
        
        # Log the error
        print(f"Unexpected error: {str(e)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.INVALID_REQUEST,
                "message": ErrorMessages.get_message(country, ErrorCode.INVALID_REQUEST),
                "country": country
            }
        ) 