from prometheus_client import Counter, Histogram, Gauge
from typing import Dict
import time

class Metrics:
    def __init__(self):
        # Country-specific metrics
        self.requests_total = Counter(
            'requests_total',
            'Total requests',
            ['country', 'endpoint']
        )
        
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['country', 'endpoint']
        )
        
        self.active_users = Gauge(
            'active_users',
            'Number of active users',
            ['country']
        )
        
        self.betting_codes_submitted = Counter(
            'betting_codes_submitted',
            'Total betting codes submitted',
            ['country', 'bookmaker']
        )
        
        self.payment_volume = Counter(
            'payment_volume',
            'Total payment volume',
            ['country', 'payment_method', 'type']
        )
        
        self.payment_success_rate = Gauge(
            'payment_success_rate',
            'Payment success rate',
            ['country', 'payment_method']
        )

    def track_request(self, country: str, endpoint: str):
        self.requests_total.labels(country=country, endpoint=endpoint).inc()

    def track_request_duration(self, country: str, endpoint: str, duration: float):
        self.request_duration.labels(
            country=country,
            endpoint=endpoint
        ).observe(duration)

    def update_active_users(self, country: str, count: int):
        self.active_users.labels(country=country).set(count)

    def track_betting_code(self, country: str, bookmaker: str):
        self.betting_codes_submitted.labels(
            country=country,
            bookmaker=bookmaker
        ).inc()

    def track_payment(
        self,
        country: str,
        payment_method: str,
        amount: float,
        type: str
    ):
        self.payment_volume.labels(
            country=country,
            payment_method=payment_method,
            type=type
        ).inc(amount)

metrics = Metrics() 