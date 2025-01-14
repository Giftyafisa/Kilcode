from typing import Dict
from app.models.transaction import Transaction
from app.core.config import settings
import httpx
from datetime import datetime, timedelta

class PaystackHandler:
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        
    async def initialize_payment(self, transaction: Transaction, email: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/transaction/initialize",
                json={
                    "email": email,
                    "amount": int(transaction.amount * 100),  # Convert to kobo
                    "reference": transaction.payment_reference,
                    "callback_url": f"{settings.FRONTEND_URL}/payment/verify"
                },
                headers={
                    "Authorization": f"Bearer {self.secret_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            raise PaymentError("Failed to initialize Paystack payment")

    async def verify_payment(self, reference: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/transaction/verify/{reference}",
                headers={"Authorization": f"Bearer {self.secret_key}"}
            )
            
            if response.status_code == 200:
                return response.json()
            raise PaymentError("Failed to verify Paystack payment") 

class USSDHandler:
    def __init__(self):
        self.banks = {
            'gtb': '*737#',
            'firstbank': '*894#',
            'uba': '*919#',
            'zenith': '*966#'
        }
    
    async def initialize_payment(self, transaction: Transaction, bank_code: str, phone: str) -> Dict:
        ussd_code = self.banks.get(bank_code.lower())
        if not ussd_code:
            raise PaymentError("Unsupported bank for USSD payment")
            
        instructions = [
            f"Dial {ussd_code} on your phone",
            "Select 'Transfer'",
            f"Enter amount: {transaction.amount}",
            f"Enter account number: {settings.MERCHANT_ACCOUNT}",
            "Enter your PIN to confirm",
            f"Use reference: {transaction.payment_reference}"
        ]
        
        return {
            "status": "pending",
            "payment_reference": transaction.payment_reference,
            "ussd_code": ussd_code,
            "instructions": instructions
        }

class OPayHandler:
    BASE_URL = "https://api.opay.ng/v1"
    
    def __init__(self):
        self.merchant_id = settings.OPAY_MERCHANT_ID
        self.secret_key = settings.OPAY_SECRET_KEY
        
    async def initialize_payment(self, transaction: Transaction, phone: str) -> Dict:
        async with httpx.AsyncClient() as client:
            payload = {
                "amount": str(transaction.amount),
                "currency": "NGN",
                "country": "NG",
                "reference": transaction.payment_reference,
                "callbackUrl": f"{settings.API_URL}/payments/opay/webhook",
                "returnUrl": f"{settings.FRONTEND_URL}/payment/status",
                "customerPhone": phone,
                "customerEmail": transaction.user.email,
                "customerName": transaction.user.name,
                "expireAt": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
            }
            
            response = await client.post(
                f"{self.BASE_URL}/payments",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.secret_key}",
                    "MerchantId": self.merchant_id
                }
            )
            
            if response.status_code == 200:
                return response.json()
            raise PaymentError("Failed to initialize OPay payment")