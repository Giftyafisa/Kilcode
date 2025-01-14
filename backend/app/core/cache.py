from typing import Optional, Any
import json
from redis import Redis
from functools import wraps
from ..core.config import settings

class RedisCache:
    def __init__(self):
        self.redis_client = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        
        # Country-specific cache settings
        self.cache_ttl = {
            'nigeria': {
                'betting_codes': 300,  # 5 minutes
                'transactions': 60,    # 1 minute
                'user_profile': 600,   # 10 minutes
                'bookmaker_odds': 30   # 30 seconds
            },
            'ghana': {
                'betting_codes': 300,
                'transactions': 60,
                'user_profile': 600,
                'bookmaker_odds': 30
            }
        }

    def get_cache_key(self, key: str, country: str) -> str:
        return f"{country}:{key}"

    async def get(self, key: str, country: str) -> Optional[Any]:
        full_key = self.get_cache_key(key, country)
        data = self.redis_client.get(full_key)
        return json.loads(data) if data else None

    async def set(
        self,
        key: str,
        value: Any,
        country: str,
        cache_type: str = 'default',
        custom_ttl: Optional[int] = None
    ):
        full_key = self.get_cache_key(key, country)
        ttl = custom_ttl or self.cache_ttl[country].get(cache_type, 300)
        self.redis_client.setex(
            full_key,
            ttl,
            json.dumps(value)
        )

    async def delete(self, key: str, country: str):
        full_key = self.get_cache_key(key, country)
        self.redis_client.delete(full_key)

cache = RedisCache()

def cached_response(cache_type: str = 'default', custom_ttl: Optional[int] = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get country from kwargs or default to nigeria
            country = kwargs.get('country', 'nigeria')
            
            # Generate cache key based on function arguments
            cache_key = f"{func.__name__}:{json.dumps(kwargs)}"
            
            # Try to get from cache
            cached_data = await cache.get(cache_key, country)
            if cached_data is not None:
                return cached_data
            
            # Execute function if not cached
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache.set(
                cache_key,
                result,
                country,
                cache_type,
                custom_ttl
            )
            
            return result
        return wrapper
    return decorator 