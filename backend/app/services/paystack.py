import httpx
from typing import Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY.strip()
        if not self.secret_key.startswith('sk_'):
            logger.error("Invalid Paystack secret key format")
            raise ValueError("Invalid Paystack secret key format")

        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cache-Control": "no-cache"
        }
        self.payment_amounts = {
            'ghana': 20000,  # GHS 200 in pesewas
            'nigeria': 2192700  # NGN 21,927 in kobo
        }

    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify transaction with Paystack"""
        try:
            logger.info(f"Verifying Paystack transaction: {reference}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Authorization header: Bearer sk_****{self.secret_key[-6:]}")
                
                response = await client.get(
                    f"{self.base_url}/transaction/verify/{reference}",
                    headers=self.headers,
                    follow_redirects=True
                )
                
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {response.headers}")
                
                if response.status_code == 401:
                    logger.error("Paystack authentication failed")
                    logger.error(f"Response body: {response.text}")
                    raise Exception("Invalid Paystack authentication")

                if response.status_code != 200:
                    error_data = response.json()
                    logger.error(f"Paystack error: {error_data}")
                    raise Exception(f"Payment verification failed: {error_data.get('message')}")

                data = response.json()
                logger.info(f"Paystack verification successful: {data}")
                return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during verification: {str(e)}")
            raise Exception("Failed to connect to payment service")
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            raise

    def validate_payment_amount(self, amount: int, country: str) -> bool:
        """Validate payment amount based on country"""
        country = country.lower()
        expected_amount = self.payment_amounts.get(country)
        if not expected_amount:
            raise ValueError(f"Invalid country: {country}")
        return amount == expected_amount

paystack = PaystackService()