from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from .transaction import TransactionType, PaymentMethod, TransactionStatus

class DateRangeStats(BaseModel):
    date: str
    count: int
    amount: float

class PaymentMethodStats(BaseModel):
    method: PaymentMethod
    count: int
    amount: float

class CountryStats(BaseModel):
    total_users: int
    active_users: int
    total_transactions: int
    total_amount: float
    payment_methods: List[PaymentMethodStats]
    transaction_types: Dict[TransactionType, int]
    transaction_status: Dict[TransactionStatus, int]
    daily_stats: List[DateRangeStats]
    weekly_stats: List[DateRangeStats]
    monthly_stats: List[DateRangeStats]

class AdminStatisticsResponse(BaseModel):
    country: str
    period: str
    timestamp: datetime
    stats: CountryStats 