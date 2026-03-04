"""
Cache backend interface and Redis implementation.
This module defines the CacheBackend interface which specifies the methods for getting and setting cache entries. It also includes a RedisCache implementation that uses Redis as the underlying caching mechanism. The RedisCache class provides methods to get and set values in Redis with a specified time-to-live (TTL). This allows for efficient caching of role and permission data in the RBAC service, improving performance by reducing database queries.
"""
from abc import ABC, abstractmethod

class CacheBackend(ABC):

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value, ttl: int):
        pass