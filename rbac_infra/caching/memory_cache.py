"""
Caching backends for RBAC Infra.
Provides in-memory and Redis-based caching implementations for role and permission data.
The InMemoryCache class is a simple implementation that stores cache entries in a Python dictionary with expiration handling. The RedisCache class uses the Redis key-value store to manage cache entries, allowing for distributed caching across multiple instances of the RBAC service. Both classes implement the CacheBackend interface defined in the caching/interfaces.py module, ensuring that they can be used interchangeably within the RBAC service for improved performance.
"""
import time
from .interfaces import CacheBackend
import redis
import json
import os

class InMemoryCache(CacheBackend):

    def __init__(self):
        self._store = {}

    def get(self, key):
        value = self._store.get(key)
        if not value:
            return None
        data, expiry = value
        if expiry < time.time():
            del self._store[key]
            return None
        return data

    def set(self, key, value, ttl):
        expiry = time.time() + ttl
        self._store[key] = (value, expiry)
    

class RedisCache(CacheBackend):

    def __init__(self, url=os.getenv("REDIS_URL", "redis://localhost:6379/0")):
        self.client = redis.Redis.from_url(url)

    def get(self, key):
        value = self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    def set(self, key, value, ttl):
        self.client.setex(key, ttl, json.dumps(value))