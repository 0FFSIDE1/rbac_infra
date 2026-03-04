"""
Cache backend interface and Redis implementation.
Defines the CacheBackend interface and provides a RedisCache implementation for caching role and permission data.
"""
from abc import ABC, abstractmethod

class CacheBackend(ABC):

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value, ttl: int):
        pass