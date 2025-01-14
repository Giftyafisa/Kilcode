from enum import Enum
from typing import Optional, Dict
from fastapi import HTTPException

class ErrorCode(str, Enum):
    # General errors
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    
    # Betting errors
    INVALID_CODE = "INVALID_CODE"
    INVALID_BOOKMAKER = "INVALID_BOOKMAKER"
    INVALID_ODDS = "INVALID_ODDS"
    INVALID_STAKE = "INVALID_STAKE"
    
    # Payment errors
    PAYMENT_FAILED = "PAYMENT_FAILED"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_PAYMENT_METHOD = "INVALID_PAYMENT_METHOD"

class CountryError(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        message: str,
        country: str,
        details: Optional[Dict] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "country": country,
                "details": details or {}
            }
        )

class ErrorMessages:
    MESSAGES = {
        "nigeria": {
            ErrorCode.INVALID_CODE: "Invalid betting code format. Example: B9J-123456-ABCD",
            ErrorCode.INVALID_BOOKMAKER: "Invalid bookmaker. Supported: Bet9ja, SportyBet, 1xBet",
            ErrorCode.PAYMENT_FAILED: "Payment failed. Please try again or contact support",
            ErrorCode.INSUFFICIENT_BALANCE: "Insufficient balance. Minimum withdrawal: ₦5,000",
            ErrorCode.INVALID_AMOUNT: "Invalid amount. Minimum deposit: ₦100"
        },
        "ghana": {
            ErrorCode.INVALID_CODE: "Invalid betting code format. Example: BW-12345678",
            ErrorCode.INVALID_BOOKMAKER: "Invalid bookmaker. Supported: Betway, SportyBet, BetPawa",
            ErrorCode.PAYMENT_FAILED: "Payment failed. Please try again or contact support",
            ErrorCode.INSUFFICIENT_BALANCE: "Insufficient balance. Minimum withdrawal: GH₵10",
            ErrorCode.INVALID_AMOUNT: "Invalid amount. Minimum deposit: GH₵1"
        }
    }

    @classmethod
    def get_message(cls, country: str, code: ErrorCode) -> str:
        return cls.MESSAGES.get(country.lower(), cls.MESSAGES["nigeria"]).get(
            code,
            "An error occurred"
        ) 