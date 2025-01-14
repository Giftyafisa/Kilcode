from typing import Dict, Any, Optional, List
import httpx
from fastapi import HTTPException
import logging
from app.core.config import settings
from datetime import datetime, timedelta
import json
import hashlib
from jinja2 import Template
import asyncio

logger = logging.getLogger(__name__)

class PaymentValidationError(Exception):
    pass

class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    async def check_health(self) -> Dict[str, Any]:
        """Check if Paystack service is available"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/ping",
                    headers=self.headers
                )
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "latency_ms": response.elapsed.total_seconds() * 1000,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Paystack health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _validate_amount(self, amount: float, currency: str) -> None:
        """Validate payment amount based on currency"""
        if currency == "NGN":
            if amount < 100:  # Minimum amount for NGN
                raise PaymentValidationError("Minimum amount for NGN is ₦100")
            if amount > 10000000:  # Maximum amount for NGN
                raise PaymentValidationError("Maximum amount for NGN is ₦10,000,000")
        elif currency == "GHS":
            if amount < 1:  # Minimum amount for GHS
                raise PaymentValidationError("Minimum amount for GHS is GH₵1")
            if amount > 100000:  # Maximum amount for GHS
                raise PaymentValidationError("Maximum amount for GHS is GH₵100,000")

    def _validate_email(self, email: str) -> None:
        """Basic email validation"""
        if not email or "@" not in email:
            raise PaymentValidationError("Invalid email address")

    async def test_payment_flow(self, email: str, country: str) -> Dict[str, Any]:
        """Test the complete payment flow"""
        try:
            # Get country config
            config = self.get_country_config(country)
            
            # Initialize payment
            init_result = await self.initialize_payment(
                email=email,
                amount=config["registration_fee"],
                currency=config["currency"],
                metadata={
                    "test": True,
                    "country": country
                }
            )
            
            # Simulate payment verification
            verify_result = await self.verify_payment(init_result["reference"])
            
            return {
                "initialization": init_result,
                "verification": verify_result,
                "config": config,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Payment flow test failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Payment flow test failed: {str(e)}"
            )

    async def initialize_payment(
        self,
        email: str,
        amount: float,
        currency: str,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Initialize a payment with Paystack with validation"""
        try:
            # Validate inputs
            self._validate_email(email)
            self._validate_amount(amount, currency)
            
            # Add timestamp and tracking to metadata
            metadata = metadata or {}
            metadata.update({
                "initiated_at": datetime.utcnow().isoformat(),
                "currency": currency,
                "client_ip": metadata.get("client_ip", "unknown"),
                "user_agent": metadata.get("user_agent", "unknown")
            })
            
            # Amount should be in kobo (NGN) or pesewas (GHS)
            amount_in_minor = int(amount * 100)
            
            payload = {
                "email": email,
                "amount": amount_in_minor,
                "currency": currency,
                "callback_url": callback_url or settings.PAYSTACK_CALLBACK_URL,
                "metadata": metadata,
                "channels": self.get_country_config(
                    "nigeria" if currency == "NGN" else "ghana"
                )["channels"]
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(
                        f"{self.base_url}/transaction/initialize",
                        json=payload,
                        headers=self.headers
                    )
                    response.raise_for_status()
                    data = response.json()

                    if not data["status"]:
                        logger.error(f"Paystack error: {data.get('message')}")
                        raise PaymentValidationError(data.get("message", "Payment initialization failed"))

                    logger.info(f"Payment initialized successfully for {email}")
                    return {
                        "authorization_url": data["data"]["authorization_url"],
                        "access_code": data["data"]["access_code"],
                        "reference": data["data"]["reference"]
                    }

                except httpx.TimeoutException:
                    logger.error("Paystack API timeout")
                    raise HTTPException(
                        status_code=504,
                        detail="Payment service timeout. Please try again."
                    )
                except httpx.HTTPError as e:
                    logger.error(f"Paystack HTTP error: {str(e)}")
                    raise HTTPException(
                        status_code=502,
                        detail="Payment service unavailable. Please try again later."
                    )

        except PaymentValidationError as e:
            logger.warning(f"Payment validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error during payment initialization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred. Please try again later."
            )

    async def verify_payment(self, reference: str) -> Dict[str, Any]:
        """Verify a payment with Paystack with enhanced error handling"""
        try:
            if not reference:
                raise PaymentValidationError("Payment reference is required")

            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.get(
                        f"{self.base_url}/transaction/verify/{reference}",
                        headers=self.headers
                    )
                    response.raise_for_status()
                    data = response.json()

                    if not data["status"]:
                        logger.error(f"Payment verification failed: {data.get('message')}")
                        raise PaymentValidationError(data.get("message", "Payment verification failed"))

                    payment_data = data["data"]
                    status = payment_data["status"]
                    
                    # Enhanced status validation
                    if status not in ["success", "failed", "abandoned"]:
                        logger.warning(f"Unexpected payment status: {status}")
                        raise PaymentValidationError("Invalid payment status")

                    logger.info(f"Payment verified successfully: {reference}")
                    return {
                        "status": status,
                        "amount": payment_data["amount"] / 100,
                        "currency": payment_data["currency"],
                        "reference": payment_data["reference"],
                        "metadata": payment_data.get("metadata", {}),
                        "paid_at": payment_data.get("paid_at"),
                        "channel": payment_data.get("channel"),
                        "card_type": payment_data.get("authorization", {}).get("card_type")
                    }

                except httpx.TimeoutException:
                    logger.error("Verification timeout")
                    raise HTTPException(
                        status_code=504,
                        detail="Verification service timeout. Please try again."
                    )
                except httpx.HTTPError as e:
                    logger.error(f"Verification HTTP error: {str(e)}")
                    raise HTTPException(
                        status_code=502,
                        detail="Verification service unavailable. Please try again later."
                    )

        except PaymentValidationError as e:
            logger.warning(f"Payment verification validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error during payment verification: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during verification."
            )

    def get_country_config(self, country: str) -> Dict[str, Any]:
        """Get country-specific configuration"""
        configs = {
            "nigeria": {
                "currency": "NGN",
                "registration_fee": 16256,  # ₦16,256
                "channels": ["card", "bank", "ussd", "qr", "bank_transfer"],
                "min_amount": 100,
                "max_amount": 10000000
            },
            "ghana": {
                "currency": "GHS",
                "registration_fee": 150,  # GH₵150
                "channels": ["card", "bank", "mobile_money"],
                "min_amount": 1,
                "max_amount": 100000
            }
        }
        
        country_config = configs.get(country.lower())
        if not country_config:
            logger.warning(f"Invalid country specified: {country}")
            raise HTTPException(
                status_code=400,
                detail="Invalid country specified"
            )
            
        return country_config

    async def generate_receipt(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a payment receipt"""
        receipt_template = """
        KILCODE PAYMENT RECEIPT
        ----------------------
        Receipt No: {{ receipt_number }}
        Date: {{ timestamp }}
        
        Payment Details:
        - Amount: {{ currency_symbol }}{{ amount }}
        - Reference: {{ reference }}
        - Status: {{ status }}
        - Payment Method: {{ payment_method }}
        
        Customer Details:
        - Name: {{ customer_name }}
        - Email: {{ customer_email }}
        - Country: {{ country }}
        
        Payment Purpose: {{ purpose }}
        
        Thank you for your payment!
        ----------------------
        """
        
        template = Template(receipt_template)
        currency_symbols = {"NGN": "₦", "GHS": "GH₵"}
        
        receipt_data = {
            "receipt_number": f"RCP-{hashlib.md5(payment_data['reference'].encode()).hexdigest()[:8].upper()}",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "currency_symbol": currency_symbols.get(payment_data["currency"], ""),
            "amount": payment_data["amount"],
            "reference": payment_data["reference"],
            "status": payment_data["status"],
            "payment_method": payment_data.get("channel", "Unknown"),
            "customer_name": payment_data.get("metadata", {}).get("customer_name", "N/A"),
            "customer_email": payment_data.get("metadata", {}).get("customer_email", "N/A"),
            "country": payment_data.get("metadata", {}).get("country", "N/A"),
            "purpose": payment_data.get("metadata", {}).get("purpose", "Registration Payment")
        }
        
        return {
            "receipt_number": receipt_data["receipt_number"],
            "content": template.render(**receipt_data),
            "timestamp": receipt_data["timestamp"],
            "payment_data": payment_data
        }

    async def get_payment_analytics(
        self,
        country: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get payment analytics for a specific country"""
        try:
            start_date = start_date or (datetime.utcnow() - timedelta(days=30))
            end_date = end_date or datetime.utcnow()

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/transaction/totals",
                    headers=self.headers,
                    params={
                        "from": start_date.strftime("%Y-%m-%d"),
                        "to": end_date.strftime("%Y-%m-%d")
                    }
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "total_transactions": data["data"]["total_transactions"],
                    "successful_transactions": data["data"]["successful_transactions"],
                    "total_volume": data["data"]["total_volume"] / 100,  # Convert to major currency
                    "pending_transfers": data["data"]["pending_transfers"],
                    "unique_customers": data["data"]["unique_customers"],
                    "period": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    }
                }

        except Exception as e:
            logger.error(f"Failed to get payment analytics: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve payment analytics"
            )

    async def retry_payment(
        self,
        reference: str,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None
    ) -> Dict[str, Any]:
        """Retry a failed payment"""
        max_retries = max_retries or self.max_retries
        retry_delay = retry_delay or self.retry_delay
        attempts = 0
        last_error = None

        while attempts < max_retries:
            try:
                # Verify current payment status
                payment_data = await self.verify_payment(reference)
                
                if payment_data["status"] == "success":
                    return {
                        "status": "success",
                        "message": "Payment successful",
                        "data": payment_data
                    }
                
                # If payment failed, initialize a new payment
                if payment_data["status"] in ["failed", "abandoned"]:
                    new_payment = await self.initialize_payment(
                        email=payment_data["metadata"].get("customer_email"),
                        amount=payment_data["amount"],
                        currency=payment_data["currency"],
                        metadata={
                            "retry_of": reference,
                            "retry_attempt": attempts + 1,
                            **payment_data["metadata"]
                        }
                    )
                    
                    return {
                        "status": "retried",
                        "message": "New payment initialized",
                        "original_reference": reference,
                        "new_payment": new_payment
                    }

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Payment retry attempt {attempts + 1} failed: {last_error}")
                await asyncio.sleep(retry_delay)
                
            attempts += 1

        raise HTTPException(
            status_code=500,
            detail=f"Payment retry failed after {attempts} attempts. Last error: {last_error}"
        )

    async def run_payment_tests(self, email: str, country: str) -> Dict[str, Any]:
        """Run comprehensive payment tests"""
        test_results = []
        config = self.get_country_config(country)

        # Test cases
        test_cases = [
            {
                "name": "Valid Registration Payment",
                "amount": config["registration_fee"],
                "currency": config["currency"],
                "expected_status": "success"
            },
            {
                "name": "Below Minimum Amount",
                "amount": config["min_amount"] - 1,
                "currency": config["currency"],
                "expected_status": "error"
            },
            {
                "name": "Above Maximum Amount",
                "amount": config["max_amount"] + 1,
                "currency": config["currency"],
                "expected_status": "error"
            },
            {
                "name": "Invalid Currency",
                "amount": config["registration_fee"],
                "currency": "USD",
                "expected_status": "error"
            }
        ]

        for test_case in test_cases:
            try:
                result = await self.initialize_payment(
                    email=email,
                    amount=test_case["amount"],
                    currency=test_case["currency"],
                    metadata={"test_case": test_case["name"]}
                )
                
                test_results.append({
                    "test_case": test_case["name"],
                    "expected_status": test_case["expected_status"],
                    "actual_status": "success",
                    "result": result,
                    "passed": test_case["expected_status"] == "success"
                })
                
            except Exception as e:
                test_results.append({
                    "test_case": test_case["name"],
                    "expected_status": test_case["expected_status"],
                    "actual_status": "error",
                    "error": str(e),
                    "passed": test_case["expected_status"] == "error"
                })

        return {
            "total_tests": len(test_results),
            "passed_tests": len([t for t in test_results if t["passed"]]),
            "failed_tests": len([t for t in test_results if not t["passed"]]),
            "results": test_results,
            "timestamp": datetime.utcnow().isoformat()
        }

paystack_service = PaystackService() 