from enum import Enum

class PaymentMethod(str, Enum):
    MTN_MOMO = "mtn_momo"
    VODAFONE_CASH = "vodafone_cash"
    AIRTELTIGO = "airteltigo"
    PAYSTACK = "paystack"

class PaymentHandler:
    @staticmethod
    def get_available_methods(country: str) -> list[PaymentMethod]:
        country = country.lower()
        if country == "ghana":
            return [
                PaymentMethod.MTN_MOMO,
                PaymentMethod.VODAFONE_CASH,
                PaymentMethod.AIRTELTIGO
            ]
        elif country == "nigeria":
            return [PaymentMethod.PAYSTACK]
        return [] 