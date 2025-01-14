from typing import Dict, List
from fastapi import HTTPException
from app.models.transaction import Transaction
from app.services.payments.nigeria import PaystackHandler, USSDHandler, OPayHandler
from app.services.payments.ghana import MobileMoneyHandler, ZeepayHandler
from app.core.country_config import CountryConfig

class PaymentService:
    @staticmethod
    async def initialize_payment(
        transaction: Transaction,
        user_country: str,
        user_email: str,
        user_phone: str,
        **kwargs
    ) -> Dict:
        try:
            if user_country.lower() == 'nigeria':
                handlers = {
                    'paystack': lambda: PaystackHandler().initialize_payment(transaction, user_email),
                    'ussd': lambda: USSDHandler().initialize_payment(transaction, kwargs.get('bank_code'), user_phone),
                    'opay': lambda: OPayHandler().initialize_payment(transaction, user_phone)
                }
            elif user_country.lower() == 'ghana':
                handlers = {
                    'mtn_momo': lambda: MobileMoneyHandler('mtn_momo').initialize_payment(transaction, user_phone),
                    'vodafone_cash': lambda: MobileMoneyHandler('vodafone_cash').initialize_payment(transaction, user_phone),
                    'airtel_money': lambda: MobileMoneyHandler('airtel_money').initialize_payment(transaction, user_phone),
                    'zeepay': lambda: ZeepayHandler().initialize_payment(transaction, user_phone)
                }
            else:
                raise HTTPException(status_code=400, detail="Unsupported country")

            handler = handlers.get(transaction.payment_method)
            if not handler:
                raise HTTPException(status_code=400, detail=f"Unsupported payment method: {transaction.payment_method}")

            return await handler()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def get_available_methods(country: str, transaction_type: str) -> List[Dict]:
        config = CountryConfig.get_config(country)
        return config['payment_methods'][transaction_type] 