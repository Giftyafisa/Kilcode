from typing import Dict
from app.models.transaction import Transaction
from app.core.config import settings
import httpx

class MobileMoneyHandler:
    def __init__(self, provider: str):
        self.provider = provider
        self.providers = {
            'mtn_momo': {
                'name': 'MTN Mobile Money',
                'api_url': settings.MTN_MOMO_API_URL,
                'api_key': settings.MTN_MOMO_API_KEY
            },
            'vodafone_cash': {
                'name': 'Vodafone Cash',
                'api_url': settings.VODAFONE_API_URL,
                'api_key': settings.VODAFONE_API_KEY
            },
            'airtel_money': {
                'name': 'AirtelTigo Money',
                'api_url': settings.AIRTEL_API_URL,
                'api_key': settings.AIRTEL_API_KEY
            }
        }
        
    async def initialize_payment(self, transaction: Transaction, phone: str) -> Dict:
        provider_config = self.providers.get(self.provider)
        if not provider_config:
            raise PaymentError(f"Unsupported provider: {self.provider}")
            
        async with httpx.AsyncClient() as client:
            payload = {
                "amount": str(transaction.amount),
                "currency": "GHS",
                "phone": phone,
                "reference": transaction.payment_reference,
                "callback_url": f"{settings.API_URL}/payments/{self.provider}/webhook",
                "return_url": f"{settings.FRONTEND_URL}/payment/status"
            }
            
            response = await client.post(
                f"{provider_config['api_url']}/payments",
                json=payload,
                headers={
                    "Authorization": f"Bearer {provider_config['api_key']}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return {
                    "status": "pending",
                    "payment_reference": transaction.payment_reference,
                    "provider_reference": response.json().get("provider_reference"),
                    "instructions": [
                        f"You will receive a prompt on your {provider_config['name']} registered number",
                        "Enter your PIN to authorize the payment",
                        "Wait for confirmation message"
                    ]
                }
            raise PaymentError(f"Failed to initialize {provider_config['name']} payment")

class ZeepayHandler:
    def __init__(self):
        self.api_url = settings.ZEEPAY_API_URL
        self.api_key = settings.ZEEPAY_API_KEY
        
    async def initialize_payment(self, transaction: Transaction, phone: str) -> Dict:
        async with httpx.AsyncClient() as client:
            payload = {
                "amount": str(transaction.amount),
                "currency": "GHS",
                "phone": phone,
                "reference": transaction.payment_reference,
                "callback_url": f"{settings.API_URL}/payments/zeepay/webhook"
            }
            
            response = await client.post(
                f"{self.api_url}/payments",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            raise PaymentError("Failed to initialize Zeepay payment") 