from fastapi import Request
from fastapi.responses import JSONResponse
from ...core.errors import CountryError, ErrorCode, ErrorMessages

class PaymentErrorHandler:
    @staticmethod
    async def handle_payment_error(request: Request, error: Exception) -> JSONResponse:
        country = request.path_params.get("country", "nigeria")
        
        if isinstance(error, ValueError):
            return JSONResponse(
                status_code=400,
                content={
                    "code": ErrorCode.INVALID_AMOUNT,
                    "message": ErrorMessages.get_message(country, ErrorCode.INVALID_AMOUNT),
                    "country": country
                }
            )
            
        # Handle payment provider specific errors
        if country.lower() == "nigeria":
            if "Paystack" in str(error):
                return JSONResponse(
                    status_code=400,
                    content={
                        "code": ErrorCode.PAYMENT_FAILED,
                        "message": "Paystack payment failed. Please try again.",
                        "country": country
                    }
                )
        elif country.lower() == "ghana":
            if "MTN" in str(error):
                return JSONResponse(
                    status_code=400,
                    content={
                        "code": ErrorCode.PAYMENT_FAILED,
                        "message": "MTN Mobile Money payment failed. Please try again.",
                        "country": country
                    }
                )
            
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.PAYMENT_FAILED,
                "message": ErrorMessages.get_message(country, ErrorCode.PAYMENT_FAILED),
                "country": country
            }
        )

class BettingErrorHandler:
    @staticmethod
    async def handle_betting_error(request: Request, error: Exception) -> JSONResponse:
        country = request.path_params.get("country", "nigeria")
        
        if "invalid code" in str(error).lower():
            return JSONResponse(
                status_code=400,
                content={
                    "code": ErrorCode.INVALID_CODE,
                    "message": ErrorMessages.get_message(country, ErrorCode.INVALID_CODE),
                    "country": country
                }
            )
            
        if "invalid bookmaker" in str(error).lower():
            return JSONResponse(
                status_code=400,
                content={
                    "code": ErrorCode.INVALID_BOOKMAKER,
                    "message": ErrorMessages.get_message(country, ErrorCode.INVALID_BOOKMAKER),
                    "country": country
                }
            )
            
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.INVALID_REQUEST,
                "message": ErrorMessages.get_message(country, ErrorCode.INVALID_REQUEST),
                "country": country
            }
        ) 