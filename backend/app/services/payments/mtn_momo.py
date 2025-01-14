import os
import uuid
from typing import Optional
import httpx
from fastapi import HTTPException

class MTNMoMoService:
    def __init__(self):
        self.api_url = os.getenv('MTN_API_URL', 'https://sandbox.momodeveloper.mtn.com')
        self.subscription_key = os.getenv('MTN_SUBSCRIPTION_KEY')
        self.api_user = os.getenv('MTN_API_USER')
        self.api_key = os.getenv('MTN_API_KEY')
        self.environment = os.getenv('ENVIRONMENT', 'sandbox')

    async def get_auth_token(self) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/collection/token/",
                    headers={
                        'Ocp-Apim-Subscription-Key': self.subscription_key,
                        'Authorization': f"Basic {self._get_basic_auth()}"
                    }
                )
                response.raise_for_status()
                return response.json()['access_token']
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Failed to get MTN auth token: {str(e)}")

    async def initialize_payment(self, amount: float, phone: str, currency: str = 'GHS', description: Optional[str] = None) -> dict:
        reference = f"TX-{uuid.uuid4()}"
        
        payment_request = {
            "amount": str(amount),
            "currency": currency,
            "externalId": reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone.replace('+', '')
            },
            "payerMessage": description or f"Payment of {currency} {amount}",
            "payeeNote": f"Withdrawal request for {phone}"
        }

        try:
            token = await self.get_auth_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/collection/v1_0/requesttopay",
                    json=payment_request,
                    headers={
                        'X-Reference-Id': reference,
                        'X-Target-Environment': self.environment,
                        'Ocp-Apim-Subscription-Key': self.subscription_key,
                        'Authorization': f"Bearer {token}",
                        'Content-Type': 'application/json'
                    }
                )
                response.raise_for_status()
                
                return {
                    "status": "pending",
                    "reference": reference,
                    "amount": amount,
                    "currency": currency,
                    "phone": phone
                }

        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"MTN MoMo payment failed: {str(e)}")

    def _get_basic_auth(self) -> str:
        import base64
        credentials = f"{self.api_user}:{self.api_key}"
        return base64.b64encode(credentials.encode()).decode() 